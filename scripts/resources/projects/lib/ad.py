from ldap3 import Server, Connection, ALL, LEVEL
from . import log

def connect(host,u,p):
    """
    Setup LDAP to Host. Takes arguments
    * host (ip/dns of domain controller)
    * username with domain in DOMAIN\\Username writing
    * password of user
    returns connection object
    """

    s = Server(host,
               get_info=ALL)
    c = Connection(s,
                   user=u,
                   password=p,
                   read_only=True)
    return c


def openstack_groups(conn):
    """
    Gets all groups which should be made in stack. Takes:
    * connection object
    Returns array of group names
    """
    groups = []
    conn.search(attributes=['Name'],
                    search_scope=LEVEL,
                    search_base='ou=OpenStack,ou=Resources,ou=Groepen,dc=nnm,dc=local',
                    search_filter='(objectclass=group)')
    for g in conn.entries:
        if str(g['Name'])[:12] == 'Openstack - ':
            groups.append(str(g['Name']))
        else:
            log.logger.warning("%s is not a good group name. Should start with 'Openstack - '" % g['Name'])
    return groups

def openstack_users(conn):
    """
    Get all openstack users allowed to openstack. Takes:
    * connection object
    Returns a array of hashes with keys: mail, username, firstname, lastname and DN
    """
    users = []
    conn.search(attributes=['givenName','sn','mail','distinguishedName'],
                search_scope=LEVEL,
                search_base='ou=NNM Users,dc=nnm,dc=local',
                search_filter='(&(objectclass=user)(memberOf:1.2.840.113556.1.4.1941:=CN=Team - Openstack,OU=Teams,OU=Organisatie,OU=Groepen,DC=nnm,DC=local))')
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

def openstack_users_in_group(conn,group):
    """
    Gets all openstack users in a group. Takes:
    * connection object
    * group name
    """
    users = []
    conn.search(attributes=['mail'],
                search_base='dc=nnm,dc=local',
                search_filter='(&(objectclass=user)(memberof:1.2.840.113556.1.4.1941:=CN=Team - Openstack,OU=Teams,OU=Organisatie,OU=Groepen,DC=nnm,DC=local)(memberOf:1.2.840.113556.1.4.1941:=CN='+group+',OU=OpenStack,OU=Resources,OU=Groepen,DC=nnm,DC=local))')

    for u in conn.entries:
        users.append(str(u['mail']).split("@")[0].lower())
    return users


##### All below probally depreciaded

def user_member_of(conn,dn):
    """
    Get all groups user in member of. Takes arguments
    * connection object
    * Full DN of user
    Returns array of groups
    """
    groups = []
    conn.search(attributes=['Name'],
                search_base='dc=nnm,dc=local',
                search_filter='(&(Name=Map*)(member:1.2.840.113556.1.4.1941:='+dn+'))')
    for g in conn.entries:
        groups.append(str(g['name']))
    return groups

def groups_in_group(conn,groupname):
    """
    Get all groups (also nested) in a group nested in the Openstack OU. Takes:
    * connection object
    * Groupname
    Returns array of groups
    """
    groups = []
    conn.search(attributes=['Name'],
                search_base='dc=nnm,dc=local',
                search_filter='(&(objectclass=group)(memberOf:1.2.840.113556.1.4.1941:=CN='+groupname+',OU=OpenStack,OU=Resources,OU=Groepen,DC=nnm,DC=local))')
    for g in conn.entries:
        if str(g['Name'])[:12] == 'Openstack - ':
            groups.append(str(g['Name']))
        else:
            log.logger.warning("%s is not a good group name. Should start with 'Openstack - '" % g['Name'])



    return groups

def gather_ad_groups(conn):
    """
    Gets all Openstack allowed groups and sets Keystone name. Takes:
    * connection object
    Returns array of groups
    """
    grp = []
    for g in  get_openstack_groups(conn):
        if g[:12] != 'Openstack - ':
            log.logger.warning("%s is not a good group name" % g)
            continue
        grp.append('adsync - %s' % g[12:])
    return grp

def users_in_group(conn,groupname):
    """
    Gets all users in a group in the Openstack OU. Takes
    * connection object
    * Group name
    Returns a array of hashes with keys: mail, username, firstname, lastname and DN
    """
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
