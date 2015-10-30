#!/usr/bin/env python2.7
from keystoneclient.auth.identity import v3
from keystoneclient import session
from keystoneclient.v3 import client
from os import environ

auth = v3.Password(auth_url="https://stack.naturalis.nl:5000/v3",
                   username=environ['OS_USERNAME'],
                   password=environ['OS_PASSWORD'],
                   project_name=environ['OS_PROJECT_NAME'],
                   user_domain_name='Default',
                   project_domain_id='Default')

sess = session.Session(auth=auth,verify='~/projects/stack.naturalis.nl/cert/stack_naturalis_nl.ca-bundle')

ks = client.Client(session=sess)
users = ks.users.list()
for u in users:
        print u.name
groups = ks.groups.list()
print groups
