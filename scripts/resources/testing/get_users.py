#!/usr/bin/env python2.7

from keystoneclient.auth.identity import v3
from keystoneclient import session
from keystoneclient.v3 import client
from os import environ


auth = v3.Password(auth_url=environ['OS_AUTH_URL'],
                   username=environ['OS_USERNAME'],
                   password=environ['OS_PASSWORD'],
                   project_name=environ['OS_PROJECT_NAME'],
                   user_domain_name='Default')

sess = session.Session(auth=auth)


ks = client.Client(session=sess)
users = ks.users.list()
print users
