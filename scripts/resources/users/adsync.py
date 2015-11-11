#!/usr/bin/python2.7

from os import environ


from lib import ad as ad
from lib import ks as ks
from lib import log as log
from lib import config as config

# Rewrite of user originisation
# All stack users are in Team - Openstack
# There are Groups in de Openstack OU
# These groups create groups in Keystone and are used for membership
# The combination of users in a Opensack - Group AND in Team - Openstack creates a user

host = '10.21.1.74'
ks_ad_group_sync_id = 'ae41c863c3474201957e330885deda5e'


auth_url = 'http://' + config.get('admin_endpoint_ip') + ':35357/v3'
ks_username = config.get('os_username')
ks_password = config.get('os_password')
project_name = config.get('os_project_name')
user = config.get('ad_user')
password = config.get('ad_password')
domain = config.get('ad_domain')
to_address = config.get('account_mail_to') 

# try:
#     user = environ['AD_USER']
#     password = environ['AD_PASS']
# except KeyError as e:
#     print "ERROR: create export of AD_USER (without domain) en AD_PASS to authenicate"
#     exit(1)
#
# try:
#     auth_url = environ['KS_ENDPOINT_V3']
#     ks_username = environ['OS_USERNAME']
#     ks_password = environ['OS_PASSWORD']
#     project_name = environ['OS_PROJECT_NAME']
# except KeyError as e:
#     print "ERROR: export of var KS_ENDPOINT_V3, OS_USERNAME, OS_PASSWORD and OS_PROJECT_NAME should exist"
#     exit(1)

# try:
#     to_address = environ['KS_MAILTO']
# except KeyError as e:
#     print "ERROR: export of var KS_MAILTO should exist"
#     exit(1)

#domain = "NNM\\"
c = ad.connect(host,domain+user,password)
ksclient = ks.connect(auth_url,ks_username,ks_password,project_name)


def sync_users():

    all_users = ad.openstack_users(c)
    ks_users = [u.name for u in ksclient.users.list(group=ks_ad_group_sync_id,enabled=True)]
    ks_users_disabled = [u.name for u in ksclient.users.list(group=ks_ad_group_sync_id,enabled=False)]
    added_users = [x for x in all_users if x['username'] not in ks_users]
    disabled_users = [x for x in ks_users if x not in [q['username'] for q in all_users]]

    for u in added_users:
        log.logger.debug("Checking if %s already exists : %s" % ( u['username'], str(ks.user_exists(ksclient,u['username']))))
        if ks.user_exists(ksclient,u['username']):  # So user already exists what should we do
                if u['username'] in ks_users_disabled: # so user is in the list of disabled users and in the ad sync group
                    log.logger.debug("Trying to enable user %s" % u['username'])
                    ####
                    if ks.enable_user(ksclient,u['username']):
                       log.logger.info("Succesfully enabled user %s" % u['username'])
                    else:
                       log.logger.error("Unable to enable user %s" % u['username'])
                    ####
                else: # user is disabled but not in ad sync group
                    log.logger.info("don't do anything, user %s exists but not in ad sync group" % u['username'])
        else:
            log.logger.debug("Trying to create user %s" % u['username'])
            ####
            if ks.create_user(ksclient,u['username'],ks_ad_group_sync_id,to_address):
                log.logger.info("Succesfully to created user %s" % u['username'])
            else:
                log.logger.error("Unable to create user %s" % u['username'])
            ####

    for u in disabled_users:
        log.logger.debug("Trying to disable user: %s" % u)
        ####
        if ks.disable_user(ksclient,u):
            log.logger.info("Succesfully disabled user %s" % u)
        else:
            log.logger.error("Unable to disable user %s" % u)
        ####

def sync_groups():
    ad_groups = []
    for g in ad.openstack_groups(c):
        ad_groups.append(str(g).replace('Openstack - ','adsync - '))
    ks_group_list = [g.name for g in ksclient.groups.list() if g.name[:9] == 'adsync - ']
    ad_added_groups = [x for x in ad_groups if x not in ks_group_list]
    ad_removed_groups = [x for x in ks_group_list if x not in ad_groups]

    for g in ad_added_groups:
        log.logger.debug("Trying to add group %s" % g)
        ####
        if ks.create_group(ksclient,g):
            log.logger.info("Succesfully created group %s" % g)
        else:
            log.logger.error("Unable to create group %s" % g)
        ####
    for g in ad_removed_groups:
        log.logger.debug("Trying to remove group %s" % g)
        ####
        if ks.delete_group(ksclient,g):
            log.logger.info("Succesfully deleted group %s" % g)
        else:
            log.logger.error("Unable to delete group %s" % g)
        ####
def sync_membership():

    for i in ad.openstack_groups(c):
        log.logger.debug("Syncing group: adsync - %s" % i[12:])
        #users_ad = [ u['username'] for u in ad.users_in_group(c,i) ]
        users_ad = [ u for u in ad.openstack_users_in_group(c,i) ]
        if ks.get_id_ks_group(ksclient,"adsync - %s" % i[12:]):
            users_ks = [u.name for u in ksclient.users.list(group=ks.get_id_ks_group(ksclient,"adsync - %s" % i[12:]))]
            added = [x for x in users_ad if x not in users_ks]
            removed = [x for x in users_ks if x not in users_ad]

            for u in added:
                log.logger.debug("Trying to add user %s to group %s" % (u,"adsync - %s" % i[12:]))
                ####
                if ks.add_user_to_group(ksclient,"adsync - %s" % i[12:],u):
                    log.logger.info("Added user %s to group %s" % (u,"adsync - %s" % i[12:]))
                else:
                    log.logger.error("Adding user %s to group %s failed" % (u,"adsync - %s" % i[12:]))
                ####
            for u in removed:
                log.logger.debug("Trying to remove user %s from group %s" % (u,"adsync - %s" % i[12:]))
                ####
                if ks.remove_user_from_group(ksclient,"adsync - %s" % i[12:],u):
                    log.logger.info("Removed user %s to group %s" % (u,"adsync - %s" % i[12:]))
                else:
                    log.logger.error("Removing user %s to group %s failed" % (u,"adsync - %s" % i[12:]))
                ####
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
