#!/usr/bin/python2.7

import yaml
from os import environ, listdir
from os.path import isfile,join
from lib.keystone import KeyStone
from lib.nova import Nova
from lib.cinder import Cinder
from lib.neutron import Neutron

from glob import glob
from lib import log

try:
    auth_url = environ['KS_ENDPOINT_V3']
    auth_url_v2 = environ['KS_ENDPOINT_V2']
    ks_username = environ['OS_USERNAME']
    ks_password = environ['OS_PASSWORD']
    project_name = environ['OS_PROJECT_NAME']
except KeyError as e:
    print "ERROR: export of var KS_ENDPOINT_V3, OS_USERNAME, OS_PASSWORD and OS_PROJECT_NAME should exist"
    exit(1)

keystone = KeyStone(auth_url,ks_username,ks_password,project_name)

nova = Nova(auth_url_v2,ks_username,ks_password,project_name)
cinder = Cinder(auth_url_v2,ks_username,ks_password,project_name)
neutron = Neutron(auth_url_v2,ks_username,ks_password,project_name)

project_files = [ join('projects.d',f) for f in listdir('projects.d') if (isfile(join('projects.d',f)) and f[-5:] == '.yaml') ]

flavors_to_projects = {}


for pf in project_files:
    log.logger.debug("Using filename: %s" % pf)
    with open(pf) as f:
        data = yaml.safe_load(f)['project']
        f.close()

    if not keystone.check_if_project_excists(data['name']):
        log.logger.debug("Create project name '%s'" % data['name'])
        keystone.create_project(data['name'])

    keystone.update_access_to_project(data['name'], data['groups'])

    qu = nova.update_quota(keystone.project_name_to_id(data['name']), data['quotas']['nova'])
    if qu:
        log.logger.info("Succesfully updated nova quota of %s with %s" % (data['name'], data['quotas']['nova']))
    elif qu is None:
        log.logger.info("No need to update nova quota of %s" % data['name'])
    else:
        log.logger.warning("Failed to update nova quota for %s" % data['name'])

    neutron.testy(keystone.project_name_to_id(data['name']))
    #neutron.update_quota(keystone.project_name_to_id(data['name']), data['quotas']['neutron'])

    log.logger.debug("Generate falvor accces by project dictionary")
    for fl in data['flavors']:
        if flavors_to_projects.get(fl):
            flavors_to_projects[fl].append(data['name'])
        else:
            flavors_to_projects[fl] = [data['name']]



for key,value in flavors_to_projects.iteritems():

    excludes = ['SNB','admin']
    try:
        current = []
        if nova.flavor_access(key) is not None:
            for c in nova.flavor_access(key):
                current.append(keystone.project_id_to_name(c.tenant_id))

        added = [a for a in value if a not in current]
        removed = [ r for r in current if (r not in value and r not in excludes)]

        #print "Added: %s" % added
        for to_add in added:
            if nova.grant_to_flavor(key, keystone.project_name_to_id(to_add)):
                log.logger.info("Added %s to have access to %s" % (to_add, key))
            else:
                log.logger.warning("Failed to add %s to have acccess to %s" % (to_add, key))
        #print "Removed: %s" % removed
        for to_remove in removed:
            if nova.revoke_to_flavor(key, keystone.project_name_to_id(to_remove)):
                log.logger.info("Removed %s to have access to %s" % (to_remove, key))
            else:
                log.logger.warning("Failed to remove %s to have acccess to %s" % (to_add, key))
    except NameError as e:
        log.logger.warning("Flavor with name %s does not excist" % key)
        log.logger.debug(e)
