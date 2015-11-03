#!/usr/bin/python2.7

from os import environ


from lib import ad as ad
from lib import ks as ks
from lib import log as log
# some situations
#   user created in ad -> sync to keystone
#   then removed ad -> disabled keystone
#   added in ad -> enabled keystone


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
# def sync_lists(activedirectory,keystone):
#     added = [x for x in activedirectory if x not in keystone]
#     removed = [x for x in keystone if x not in activedirectory]
#     return {'added' : added , 'removed' : removed }

def add_users_objects(ad_user_object,keystone):
    return [x for x in ad_user_object if x['username'] not in keystone]

def disable_users(ad_user_object,keystone):
    #adusers = [u['username'] for u in ad_user_object ]
    return [x for x in keystone if x not in [u['username'] for u in ad_user_object]]

def added_groups(ad_flat_groups,ks_groups):
    return [x for x in ad_flat_groups if x not in ks_groups]

def removed_groups(ad_flat_groups,ks_groups):
    return [x for x in ks_groups if x not in ad_flat_groups]




if c.bind():
    log.logger.info('Starting user sync')
    all_users = ad.users_in_group(c,'Openstack - All Users')
    ks_users = [u.name for u in ksclient.users.list(group=ks_ad_group_sync_id,enabled=True)]
    ks_users_disabled = [u.name for u in ksclient.users.list(group=ks_ad_group_sync_id,enabled=False)]
    ks_group_list = [g.name for g in ksclient.groups.list() if g.name[:17] == 'Research Group - ']
    ad_added_groups = added_groups(ad.gather_ad_groups(c),ks_group_list)
    ad_removed_groups = removed_groups(ad.gather_ad_groups(c),ks_group_list)

    for u in add_users_objects(all_users,ks_users):
        log.logger.debug("Checking if %s already exists : %s" % ( u['username'], str(user_exists(u['username']))))
        if user_exists(u['username']):
            # So user already exists what should we do
                if u['username'] in ks_users_disabled:
                    # so user is in the list of disabled users and in the ad sync group
                    log.logger.info("Run function to enable user")
                else:
                    # user is disabled but not in ad sync group
                    log.logger.info("don't do anything, user is disabled but not in ad sync")
        else:
            log.logger.info("Run function to create user %s" % u['username'])

        #print "adding %s %s with\nUsername: %s\nMail: %s\n----------------" % (u['firstname'],u['lastname'],u['username'],u['mail'])
    for u in  disable_users(all_users,ks_users):
        log.logger.info("disable user: %s" % u)

    log.logger.info('Starting group sync')
    for g in ad_added_groups:
        log.logger.info("add group %s" % g)

    for g in ad_removed_groups:
        log.logger.info("remove group %s" % g)

    log.logger.info('Starting sync users in groups')
    for i in ad.groups_in_group(c,'Openstack - All Users'):
        log.logger.debug("Group: Research Group - %s" % i[12:])
        users_ad = [ u['username'] for u in ad.users_in_group(c,i) ]
        if get_id_ks_group("Research Group - %s" % i[12:]):
            users_ks = [u.name for u in ksclient.users.list(group=ks.get_id_ks_group("Research Group - %s" % i[12:]))]
            added = [x for x in users_ad if x not in users_ks]
            removed = [x for x in users_ks if x not in users_ad]
            log.logger.info("Added: %s" % added)
            log.logger.info("Removed: %s" % removed)
        else:
            log.logger.warning("Group %s does not excist!" % i)


c.unbind()
