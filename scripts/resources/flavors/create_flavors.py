#!/usr/bin/env python2.7

from keystoneclient.auth.identity import v2
from keystoneclient import session
from novaclient import client
from os import environ
import sys
import yaml
from lib import config
from lib import log

# allowed_types = ['ha_localdisk','hpc','ha_ceph']

# yaml_file = sys.argv[1]
# if not yaml_file[-5:] == '.yaml':
#     print "Run this as ./create_flavors yaml_file.yaml"
#     print "Dont forget to source openrc"
#     exit(1)

auth_url = 'http://' + config.get('admin_endpoint_ip') + ':35357/v3'
ks_username = config.get('os_username')
ks_password = config.get('os_password')
project_name = config.get('os_project_name')
yaml_file = config.get('flavor_yaml_file')


with open(yaml_file) as f:
    flavors = yaml.safe_load(f)
    f.close()

# for f in flavors['flavors']:
#     if f['type'] not in allowed_types:
#         print "ERROR : unknown type found, please fix before continue"
#         print "DEBUG : type: %s, cpu: %s, ram: %s  disk: %s" % (f['type'],f['cpu'],f['ram'],f['disk'])
#         print "DEBUG : allowed types: %s" % allowed_types
#         exit(1)


auth = v2.Password(auth_url=auth_url, username=ks_username, password=ks_password, tenant_name=project_name)

#sess = session.Session(auth=auth,verify='cert/stack_naturalis_nl.ca-bundle')
sess = session.Session(auth=auth)

nova = client.Client("2",session=sess)

current = []
for f in  nova.flavors.list(is_public=False):
    current.append(f.name)

inyaml = []
for f in flavors['flavors']:
    name =  "%s.%sc.%sr.%sh" % (f['type'],f['cpu'],f['ram'],f['disk'])

    if name in inyaml:
        log.logger.warning("flavor %s is duplicate in flavor.yaml so it will be skipped" % name)
        continue
    inyaml.append(name)

    if name in current:
        log.logger.warning("flavor %s exists! flavor will not be created" % name)
        continue

    log.logger.info("creating flavor %s" % name)
    flavor = nova.flavors.create(name,(f['ram']*1024),f['cpu'],f['disk'],is_public=False)
    flavor.set_keys({'type':f['type']})
