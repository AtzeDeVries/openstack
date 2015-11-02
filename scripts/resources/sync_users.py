#!/usr/bin/python2.7

from ldap3 import Server, Connection, ALL
from os import environ
from keystoneclient.auth.identity import v3
from keystoneclient import session
from keystoneclient.v3 import client

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
s = Server(host,
           get_info=ALL)
c = Connection(s,
               user=domain+user,
               password=password,
               read_only=True)

auth = v3.Password(auth_url=auth_url,
                   username=ks_username,
                   password=ks_password,
                   project_name=project_name,
                   user_domain_name='Default',
                   project_domain_id='Default')

sess = session.Session(auth=auth)

ks = client.Client(session=sess)


def sync_lists(activedirectory,keystone):
    added = [x for x in activedirectory if x not in keystone]
    removed = [x for x in keystone if x not in activedirectory]
    return {'added' : added , 'removed' : removed }

def add_users_objects(ad_user_object,keystone):
    return [x for x in ad_user_object if x['username'] not in keystone]

def disable_users(ad_user_object,keystone):
    adusers = [u['username'] for u in ad_user_object ]
    return [x for x in keystone if x not in adusers]

def user_exists(username):
    return len(ks.users.list(name=username)) != 0

def user_enabled(username):
    return ks.users.list(name=username)[0].enabled

def user_member_of(conn,dn):
    groups = []
    conn.search(attributes=['Name'],
                search_base='dc=nnm,dc=local',
                search_filter='(&(Name=Map*)(member:1.2.840.113556.1.4.1941:='+dn+'))')
    for g in conn.entries:
        groups.append(str(g['name']))

def groups_in_group(conn,groupname):
    groups = []
    conn.search(attributes=['Name'],
                search_base='dc=nnm,dc=local',
                search_filter='(&(objectclass=group)(memberOf:1.2.840.113556.1.4.1941:=CN='+groupname+',OU=OpenStack,OU=Resources,OU=Groepen,DC=nnm,DC=local))')
    for g in conn.entries:
        groups.append(str(g['Name']))

    return groups

def gather_ad_groups(conn):
    grp = []
    for g in  groups_in_group(conn,'Openstack - All users'):
        if not g[:12] == 'Openstack - ':
            print "WARNING: %s is not a good group name" % g
            continue
        grp.append('Research Group - %s' % g[12:])
    return grp

def added_groups(ad_flat_groups,ks_groups):
    return [x for x in ad_flat_groups if x not in ks_groups]

def removed_groups(ad_flat_groups,ks_groups):
    return [x for x in ks_groups if x not in ad_flat_groups]


def users_in_group(conn,groupname):
    users = []
    conn.search(attributes=['givenName','sn','mail','distinguishedName'],
                search_base='dc=nnm,dc=local',
                search_filter='(&(objectclass=Person)(memberOf:1.2.840.113556.1.4.1941:=CN='+groupname+',OU=OpenStack,OU=Resources,OU=Groepen,DC=nnm,DC=local))')
    for u in conn.entries:

        if "," in str(u['sn']):
            lastname = "%s %s" % (str(u['sn']).split(',')[1].strip(),str(u['sn']).split(',')[0].strip())
        else:
            lastname = str(u['sn'])

        users.append( {'mail': str(u['mail']).lower(),
                      'username': str(u['mail']).split("@")[0].lower(),
                      'firstname': str(u['givenName']),
                      'lastname': lastname,
                      'dn': str(u['distinguishedName'])})
    return users

def get_id_ks_group(grp):
    return ks.groups.list(name=grp)[0].id

if c.bind():
    print 'Sync these users'
    all_users = users_in_group(c,'Openstack - All Users')
    ks_users = [u.name for u in ks.users.list(group=ks_ad_group_sync_id,enabled=True)]
    ks_users_disabled = [u.name for u in ks.users.list(group=ks_ad_group_sync_id,enabled=False)]
    ks_group_list = [g.name for g in ks.groups.list() if g.name[:17] == 'Research Group - ']
    ad_added_groups = added_groups(gather_ad_groups(c),ks_group_list)
    ad_removed_groups = removed_groups(gather_ad_groups(c),ks_group_list)

    for u in add_users_objects(all_users,ks_users):
        print "Checking if %s already exists : %s" % ( u['username'], str(user_exists(u['username'])) )
        if user_exists(u['username']):
            # So user already exists what should we do
                if u['username'] in ks_users_disabled:
                    # so user is in the list of disabled users and in the ad sync group
                    print "Run function to enable user"
                else:
                    # user is disabled but not in ad sync group
                    print "don't do anything, user is disabled but not in ad sync"
        else:
            print "Run function to create user %s" % u['username']

        #print "adding %s %s with\nUsername: %s\nMail: %s\n----------------" % (u['firstname'],u['lastname'],u['username'],u['mail'])
    for u in  disable_users(all_users,ks_users):
        print "disable user: %s" % u

    for g in ad_added_groups:
        print "add group %s" % g

    for g in ad_removed_groups:
        print "remove group %s" % g

    print '\nSync users in groups'
    for i in groups_in_group(c,'Openstack - All Users'):
        print "Group: Research Group - %s" % i[12:]
        users_ad = [ u['username'] for u in users_in_group(c,i) ]
        users_ks = ks.users.list(group=get_id_ks_group("Research Group - %s" % i[12:]))
        added = [x for x in users_ad if x not in users_ks]
        removed = [x for x in users_ks if x not in users_ad]
        print "Added: %s" % added
        print "Removed: %s" % removed
        print "\n"


c.unbind()
