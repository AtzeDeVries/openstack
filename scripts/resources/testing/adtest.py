#!/usr/bin/python2.7

from ldap3 import Server, Connection, ALL
from os import environ

host = '10.21.1.74'

try:
    user = environ['AD_USER']
    password = environ['AD_PASS']
except KeyError as e:
    print "ERROR: create export of AD_USER (without domain) en AD_PASS to authenicate"
    exit(1)

domain = "NNM\\"

s = Server(host,
           get_info=ALL)
c = Connection(s,
               user=domain+user,
               password=password,
               read_only=True)

def sync_lists(activedirectory,keystone):
    added = [x for x in activedirectory if x not in keystone]
    removed = [x for x in keystone if x not in activedirectory]
    return {'added' : added , 'removed' : removed }

def add_users_objects(ad_user_object,keystone):
    return [x for x in ad_user_object if x['username'] not in keystone]

def disable_users(ad_user_object,keystone):
    adusers = [u['username'] for u in ad_user_object ]
    return [x for x in keystone if x not in adusers]


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

if c.bind():
    print 'Sync these users'
    all_users = users_in_group(c,'Openstack - All Users')
    for i in all_users:
        print i['username']

    #sync = sync_lists([u['username'] for u in all_users ],['camiel.doorenweerd','kevin.beentjes','pietje'])

    for u in add_users_objects(all_users,['kevin.beentjes','pietje']):
        print "adding %s %s with\nUsername: %s\nMail: %s\n----------------" % (u['firstname'],u['lastname'],u['username'],u['mail'])
    for u in  disable_users(all_users,['camiel.doorenweerd','kevin.beentjes','pietje']):
        print "removing user: %s" % u



    print '\nSync users in groups'
    for i in groups_in_group(c,'Openstack - All Users'):
        print i
        for u in users_in_group(c,i):
            print "* %s" % u['username']


c.unbind()
