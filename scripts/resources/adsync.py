#!/usr/bin/python2.7

from os import environ


from lib import ad as ad
from lib import ks as ks
from lib import log as log


host = '10.21.1.74'
ks_ad_group_sync_id = 'ae41c863c3474201957e330885deda5e'

try:
    user = environ['AD_USER']
    password = environ['AD_PASS']
except KeyError as e:
    print "ERROR: create export of AD_USER (without domain) en AD_PASS to authenicate"
    exit(1)

try:
    auth_url = environ['KS_ENDPOINT_V3']
    ks_username = environ['OS_USERNAME']
    ks_password = environ['OS_PASSWORD']
    project_name = environ['OS_PROJECT_NAME']
except KeyError as e:
    print "ERROR: export of var KS_ENDPOINT_V3, OS_USERNAME, OS_PASSWORD and OS_PROJECT_NAME should exist"
    exit(1)


domain = "NNM\\"
c = ad.connect(host,domain+user,password)
ksclient = ks.connect(auth_url,ks_username,ks_password,project_name)


def sync_users():

    all_users = ad.users_in_group(c,'Openstack - All Users')
    ks_users = [u.name for u in ksclient.users.list(group=ks_ad_group_sync_id,enabled=True)]
    ks_users_disabled = [u.name for u in ksclient.users.list(group=ks_ad_group_sync_id,enabled=False)]
    added_users = [x for x in all_users if x['username'] not in ks_users]
    disabled_users = [x for x in ks_users if x not in [q['username'] for q in all_users]]

    for u in added_users:
        log.logger.debug("Checking if %s already exists : %s" % ( u['username'], str(ks.user_exists(ksclient,u['username']))))
        if ks.user_exists(ksclient,u['username']):  # So user already exists what should we do
                if u['username'] in ks_users_disabled: # so user is in the list of disabled users and in the ad sync group
                    log.logger.info("Run function to enable user")
                else: # user is disabled but not in ad sync group
                    log.logger.info("don't do anything, user exists but not in ad sync group")
        else:
            log.logger.info("Run function to create user %s" % u['username'])

    for u in disabled_users:
        log.logger.info("disable user: %s" % u)


def sync_groups():

    ks_group_list = [g.name for g in ksclient.groups.list() if g.name[:17] == 'Research Group - ']
    ad_added_groups = [x for x in ad.gather_ad_groups(c) if x not in ks_group_list]
    ad_removed_groups = [x for x in ks_group_list if x not in ad.gather_ad_groups(c)]

    for g in ad_added_groups:
        log.logger.info("add group %s" % g)

    for g in ad_removed_groups:
        log.logger.info("remove group %s" % g)

def sync_membership():

    for i in ad.groups_in_group(c,'Openstack - All Users'):
        log.logger.debug("Group: Research Group - %s" % i[12:])
        users_ad = [ u['username'] for u in ad.users_in_group(c,i) ]
        if ks.get_id_ks_group(ksclient,"Research Group - %s" % i[12:]):
            users_ks = [u.name for u in ksclient.users.list(group=ks.get_id_ks_group(ksclient,"Research Group - %s" % i[12:]))]
            added = [x for x in users_ad if x not in users_ks]
            removed = [x for x in users_ks if x not in users_ad]
            log.logger.info("Added: %s" % added)
            log.logger.info("Removed: %s" % removed)
        else:
            log.logger.warning("Group %s does not available!" % i)


if c.bind():
    log.logger.info('Starting user sync')
    sync_users()
    log.logger.info('Starting group sync')
    sync_groups()
    log.logger.info('Starting sync users in groups')
    sync_membership()
c.unbind()
