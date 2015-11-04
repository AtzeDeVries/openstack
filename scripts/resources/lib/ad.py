from ldap3 import Server, Connection, ALL
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
        if not g[:12] == 'Openstack - ':
            log.logger.warning("%s is not a good group name" % g)
            continue
        groups.append(str(g['Name']))

    return groups

def gather_ad_groups(conn):
    """
    Gets all Openstack allowed groups and sets Keystone name. Takes:
    * connection object
    Returns array of groups
    """
    grp = []
    for g in  groups_in_group(conn,'Openstack - All users'):
        if not g[:12] == 'Openstack - ':
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
