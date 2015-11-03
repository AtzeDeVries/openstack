from keystoneclient.auth.identity import v3
from keystoneclient import session
from keystoneclient.v3 import client
from os import urandom
from string import ascii_letters, digits
import random
from . import log

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

def generate_password(numbers=10):
    """
    Generates complex password. Takes:
    * number of digit (default 10)
    Returns password
    """
    chars = ascii_letters + digits + '#$%^*()'
    random.seed = (urandom(1024))
    return ''.join(random.choice(chars) for i in range(numbers))


def create_user(client,username,sync_group_id):
    """
    Creates user in keystone. Takes:
    * keystone client object
    * username
    * keystone id of sync ad user group
    Returns True is succeeded, false if issues.
    """

    try:
        client.users.create(name=username,
                            email=username+'@naturalis.nl',
                            password=generate_password())
        uid = client.users.list(name=username)[0].id
        client.users.add_to_group(uid,sync_group_id)
        return True
    except Exception as e:
        log.logger.error('Unable to create user %s OR add it to group. Error: %s' % (username,e))
        return False

def enable_user(client,username):
    """
    enables user in keystone. Takes:
    * keystone client object
    * username
    Returns True is succeeded, false if issues.
    """

    try:
        uid = client.users.list(name=username)[0].id
        client.users.update(uid,enabled=True)
        return True
    except Exception as e:
        log.logger.error('Unable to enable user %s. Error: %s' % (username,e))
        return False

def disable_user(client,username):
    """
    disables user in keystone. Takes:
    * keystone client object
    * username
    Returns True is succeeded, false if issues.
    """
    try:
        uid = client.users.list(name=username)[0].id
        client.users.update(uid,enabled=False)
        return True
    except Exception as e:
        log.logger.error('Unable to disable user %s. Error: %s' % (username,e))
        return False
