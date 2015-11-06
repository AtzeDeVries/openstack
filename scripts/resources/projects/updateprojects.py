#!/usr/bin/python2.7

import yaml
from os import environ, listdir
from os.path import isfile,join
from lib.keystone import KeyStone
from glob import glob
from lib import log

try:
    auth_url = environ['KS_ENDPOINT_V3']
    ks_username = environ['OS_USERNAME']
    ks_password = environ['OS_PASSWORD']
    project_name = environ['OS_PROJECT_NAME']
except KeyError as e:
    print "ERROR: export of var KS_ENDPOINT_V3, OS_USERNAME, OS_PASSWORD and OS_PROJECT_NAME should exist"
    exit(1)

keystone = KeyStone(auth_url,ks_username,ks_password,project_name)

#print keystone.user_enabled('rutger.vos')

project_files = [ join('projects.d',f) for f in listdir('projects.d') if (isfile(join('projects.d',f)) and f[-5:] == '.yaml') ]
#project_files = glob("projects.d/*.yaml")
for pf in project_files:
    log.logger.debug("Using filename: %s" % pf)
    with open(pf) as f:
        data = yaml.safe_load(f)['project']
        f.close()
    log.logger.debug("Create project name '%s'" % data['name'])
    log.logger.debug("")
    print [flavor for flavor in data['flavors']]


    # for flavor in data['project']['flavors']:
    #     print flavor
keystone.projects.create(name = 'testproject',
                        domain = 'Default')
