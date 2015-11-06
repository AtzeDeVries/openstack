#!/usr/bin/python2.7


from os import environ
from lib import Ks

try:
    auth_url = environ['KS_ENDPOINT_V3']
    ks_username = environ['OS_USERNAME']
    ks_password = environ['OS_PASSWORD']
    project_name = environ['OS_PROJECT_NAME']
except KeyError as e:
    print "ERROR: export of var KS_ENDPOINT_V3, OS_USERNAME, OS_PASSWORD and OS_PROJECT_NAME should exist"
    exit(1)

keystone = Ks(auth_url,ks_username,ks_password,project_name)

print keystone.user_enabled('rutger.vos')
