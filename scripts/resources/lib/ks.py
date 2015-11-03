from keystoneclient.auth.identity import v3
from keystoneclient import session
from keystoneclient.v3 import client

def connect(auth_url,ks_username,ks_password,project_name):
    """
    Generates a keystone client session object. Takes:
    * Keystone V3 auth url
    * Username
    * Password
    * Project name
    returns a keystone client object.
    """
    auth = v3.Password(auth_url=auth_url,
                       username=ks_username,
                       password=ks_password,
                       project_name=project_name,
                       user_domain_name='Default',
                       project_domain_id='Default')

    sess = session.Session(auth=auth)

    return client.Client(session=sess)

def user_exists(client,username):
    """
    Checks if user exists. Takes:
    * keystone client object
    * username
    Returns bool
    """
    return len(client.users.list(name=username)) != 0

def user_enabled(client,username):
    """
    Checks if user is enabled. Takes:
    * keystone client object
    * username
    Returns bool
    """
    return client.users.list(name=username)[0].enabled



def get_id_ks_group(client,grp):
    """
    Find id of a keystone group. Takes:
    * keystone client object
    * Groupname
    Returns id (as string) or False if group not found
    """
    try:
        return ks.groups.list(name=grp)[0].id
    except:
        return False
