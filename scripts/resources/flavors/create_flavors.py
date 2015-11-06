#!/usr/bin/env python2.7

from keystoneclient.auth.identity import v2
from keystoneclient import session
from novaclient import client
from os import environ

import yaml

allowed_types = ['ha_localdisk','hpc','ha_ceph']


with open('flavor.yaml') as f:
    flavors = yaml.safe_load(f)
    f.close()

for f in flavors['flavors']:
    if f['type'] not in allowed_types:
        print "ERROR : unknown type found, please fix before continue"
        print "DEBUG : type: %s, cpu: %s, ram: %s  disk: %s" % (f['type'],f['cpu'],f['ram'],f['disk'])
        print "DEBUG : allowed types: %s" % allowed_types
        exit(1)


auth = v2.Password(
    auth_url=environ['OS_AUTH_URL'],
    username=environ['OS_USERNAME'],
    password=environ['OS_PASSWORD'],
    tenant_name=environ['OS_USERNAME']
    )

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
        print "WARNING: flavor %s is duplicate in flavor.yaml so it will be skipped" % name
        continue
    inyaml.append(name)

    if name in current:
        print "WARNING: flavor %s exists! flavor will not be created" % name
        continue

    print "creating %s" % name
    flavor = nova.flavors.create(name,(f['ram']*1024),f['cpu'],f['disk'],is_public=False)
    flavor.set_keys({'type':f['type']})
