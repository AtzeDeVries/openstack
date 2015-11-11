#!/usr/bin/python2.7

import yaml

from os import environ, listdir
from os.path import isfile,join
from glob import glob

from lib.keystone import KeyStone
from lib.nova import Nova
from lib.cinder import Cinder
from lib.neutron import Neutron
from lib import log
from lib import config

# try:
#     auth_url = environ['KS_ENDPOINT_V3']
#     auth_url_v2 = environ['OS_AUTH_URL']
#     ks_username = environ['OS_USERNAME']
#     ks_password = environ['OS_PASSWORD']
#     project_name = environ['OS_PROJECT_NAME']
# except KeyError as e:
#     print "ERROR: export of var KS_ENDPOINT_V3, OS_USERNAME, OS_PASSWORD and OS_PROJECT_NAME should exist"
#     exit(1)

#### Get settings from INI
pfd = config.get('yaml_project_dir')
auth_url = 'http://' + config.get('admin_endpoint_ip') + ':35357/v3'
auth_url_v2 = 'http://' + config.get('admin_endpoint_ip') + ':35357/v2.0'
ks_username = config.get('os_username')
ks_password = config.get('os_password')
project_name = config.get('os_project_name')
gateway_id = config.get('gateway_network_id')
ca_bundle = config.get('ca_bundle_file')

### End Settings
### start API's
keystone = KeyStone(auth_url,ks_username,ks_password,project_name)
nova = Nova(auth_url_v2,ks_username,ks_password,project_name,ca_bundle)
cinder = Cinder(auth_url_v2,ks_username,ks_password,project_name,ca_bundle)
neutron = Neutron(auth_url_v2,ks_username,ks_password,project_name,ca_bundle)

## get project files, skip default.yaml
project_files = [ join(pfd,f) for f in listdir(pfd) if (isfile(join(pfd,f)) and f[-5:] == '.yaml' and f != 'default.yaml') ]

flavors_to_projects = {}

for pf in project_files:

    ### Open YAML
    log.logger.debug("Using filename: %s" % pf)
    with open(pf) as f:
        data = yaml.safe_load(f)['project']
        f.close()

    ### Create Project
    if not keystone.check_if_project_excists(data['name']):
        log.logger.debug("Create project name '%s'" % data['name'])
        keystone.create_project(data['name'])

    ### Set access to project
    keystone.update_access_to_project(data['name'], data['groups'])
    ### Get project id
    project_id = keystone.project_name_to_id(data['name'])
    ### Set resources and Networks
    nova.update_quota(project_id, data['quotas']['nova'])
    neutron.update_quota(project_id, data['quotas']['neutron'])
    neutron.create_default_network(project_id,gateway_id,dns_servers=['172.16.51.4,172.16.51.5'])
    cinder.update_quota(project_id, data['quotas']['cinder'])
    #### Generate flavor to projects dictionary
    log.logger.debug("Generate falvor accces by project dictionary")
    for fl in data['flavors']:
        if flavors_to_projects.get(fl):
            flavors_to_projects[fl].append(data['name'])
        else:
            flavors_to_projects[fl] = [data['name']]


### run over all flavors(key) and check projects (value)
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
