#!/usr/bin/env python2.7

from keystoneclient.auth.identity import v2
from keystoneclient import session
from novaclient import client
from os import environ
import sys
import yaml
from lib import config
from lib import log


auth_url = 'http://' + config.get('admin_endpoint_ip') + ':35357/v2.0'
ks_username = config.get('os_username')
ks_password = config.get('os_password')
project_name = config.get('os_project_name')
yaml_file = config.get('flavor_yaml_file')
ca_bundle = config.get('ca_bundle_file')


with open(yaml_file) as f:
    flavors = yaml.safe_load(f)
    f.close()

auth = v2.Password(auth_url=auth_url, username=ks_username, password=ks_password, tenant_name=project_name)

sess = session.Session(auth=auth,verify=ca_bundle)

nova = client.Client("2",session=sess)

current = []
for f in  nova.flavors.list(is_public=False):
    current.append(f.name)

inyaml = []
for f in flavors['flavors']:
    name =  "%s.%sc.%sr.%sh" % (f['type'],f['cpu'],f['ram'],f['disk'])

    if name in inyaml:
        log.logger.debug("flavor %s is duplicate in flavor.yaml so it will be skipped" % name)
        continue
    inyaml.append(name)

    if name in current:
        log.logger.debug("flavor %s exists! flavor will not be created" % name)
        continue

    try:
        flavor = nova.flavors.create(name,(f['ram']*1024),f['cpu'],f['disk'],is_public=False)
        flavor.set_keys({'type':f['type']})
        log.logger.info("creating flavor %s" % name)
    except Exception as e:
        log.logger.warning("Failed to create flavor %s" % name)
        log.logger.debug(e)
