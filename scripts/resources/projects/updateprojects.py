#!/usr/bin/python2.7

import yaml
from os import environ, listdir
from os.path import isfile,join
from lib.keystone import KeyStone
from lib.nova import Nova
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
#
keystone = KeyStone(auth_url,ks_username,ks_password,project_name)
#
nova = Nova(auth_url_v2,ks_username,ks_password,project_name)

project_files = [ join('projects.d',f) for f in listdir('projects.d') if (isfile(join('projects.d',f)) and f[-5:] == '.yaml') ]

flavors_to_projects = {}

for pf in project_files:
    log.logger.debug("Using filename: %s" % pf)
    with open(pf) as f:
        data = yaml.safe_load(f)['project']
        f.close()
    log.logger.debug("Create project name '%s'" % data['name'])

    for fl in data['flavors']:
        if flavors_to_projects.get(fl):
            flavors_to_projects[fl].append(data['name'])
        else:
            flavors_to_projects[fl] = [data['name']]



for key,value in flavors_to_projects.iteritems():
    #print "\nFlavor %s has" % key
    # users that should have = value
    # current is
    current = []
    if nova.show(key) is not None:
        for c in nova.show(key):
            current.append(keystone.project_id_to_name(access[0].tenant_id))

    added = [a for a in value if a not in current]
    removed = [ r for r in current if r not in value]

    print "Added: %s" % added
    print "Removed: %s" % removed
    #
    # for pr in value:
    #     print " - %s" % pr
    # print "Current access of %s" % key
    # access = nova.show(key)
    # if access is not None:
    #     print "acces with id: %s which is groupname: %s" % (access[0].tenant_id,keystone.project_id_to_name(access[0].tenant_id))

#keystone.create_project('testproject')
#keystone.update_access_to_project('zooi',['SNB','piet','Rely','hpc_users'])
