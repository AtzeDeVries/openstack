from keystoneclient.auth.identity import v3
from keystoneclient import session
from keystoneclient.v3 import client
from os import urandom
from string import ascii_letters, digits
import random
import time
from . import log
import smtplib
from email.mime.text import MIMEText


class KeyStone:
    def __init__(self,auth_url,ks_username,ks_password,project_name):
        auth = v3.Password(auth_url=auth_url,
                           username=ks_username,
                           password=ks_password,
                           project_name=project_name,
                           user_domain_name='Default',
                           project_domain_id='Default')

        sess = session.Session(auth=auth)
        self.ksclient = client.Client(session=sess)
        self.member_role_id = self.ksclient.roles.list(name='_member_')[0].id

        log.logger.debug("enumbering access for groups in projects")
        self.grouplist = self.ksclient.groups.list()


    def user_enabled(self,username):
        """
        Checks if user is enabled. Takes:
        * username
        Returns bool
        """
        return self.ksclient.users.list(name=username)[0].enabled


    def create_project(self,projectname):
        """
        Creates a project
        : param str name: project name
        """

        group_id = self.ksclient.groups.list(name='SNB')[0].id
        admin_role_id = self.ksclient.roles.list(name='admin')[0].id

        new_project = self.ksclient.projects.create(name = projectname, domain = 'Default')
        log.logger.debug("New project created with id: %s" % new_project.id)
        log.logger.debug("Granting ADMIN access to SNB to project %s" % new_project.id)

        self.ksclient.roles.grant(admin_role_id,group=group_id,project=new_project.id)
        return new_project

    def update_access_to_project(self,project_name,group_name):
        """
        Update access to project
        : param str project_name: name of the project
        : param array group_name: array of the groups which should have access
        """
        # implementation of check access in roles.py is very strange. If user has
        # no acccess it throws an error instead of false...

        excludes = ['SNB']
        #group_id = self.ksclient.groups.list(name=group_name)[0].id
        group_access = {}
        project_id = self.ksclient.projects.list(name=project_name)[0].id
        for g in self.grouplist:
            try:
                access = self.ksclient.roles.check(self.member_role_id,group=g.id,project=project_id)
                group_access.update({g.name: True})
            else:
                group_access.update({g.name: False})

            #group_access.update({g.name: self.ksclient.roles.check(self.member_role_id,group=g.id,project=project_id)})
        log.logger.debug("groupaccess: %s" % group_access)
        # currrent_access = self.ksclient.roles.list(group=group_id, project=project_id)
        # for ca in currrent_access:
        #     print ca
    # def connect(auth_url,ks_username,ks_password,project_name):
    #     """
    #     Generates a keystone client session object. Takes:
    #     * Keystone V3 auth url
    #     * Username
    #     * Password
    #     * Project name
    #     returns a keystone client object.
    #     """
    #     auth = v3.Password(auth_url=auth_url,
    #                        username=ks_username,
    #                        password=ks_password,
    #                        project_name=project_name,
    #                        user_domain_name='Default',
    #                        project_domain_id='Default')
    #
    #     sess = session.Session(auth=auth)
    #
    #     return client.Client(session=sess)
    #
    # def user_exists(client,username):
    #     """
    #     Checks if user exists. Takes:
    #     * keystone client object
    #     * username
    #     Returns bool
    #     """
    #     return len(client.users.list(name=username)) != 0
    #

    #
    #
    # def get_id_ks_group(client,grp):
    #     """
    #     Find id of a keystone group. Takes:
    #     * keystone client object
    #     * Groupname
    #     Returns id (as string) or False if group not found
    #     """
    #     try:
    #         return client.groups.list(name=grp)[0].id
    #     except:
    #         return False
    #
    # def generate_password(numbers=10):
    #     """
    #     Generates complex password. Takes:
    #     * number of digit (default 10)
    #     Returns password
    #     """
    #     chars = ascii_letters + digits + '#$%^*()'
    #     random.seed = (urandom(1024))
    #     return ''.join(random.choice(chars) for i in range(numbers))
    #
    #
    # def create_user(client,username,sync_group_id,to_address):
    #     """
    #     Creates user in keystone. Takes:
    #     * keystone client object
    #     * username
    #     * keystone id of sync ad user group
    #     Returns True is succeeded, false if issues.
    #     """
    #
    #     try:
    #         pwd = generate_password()
    #         client.users.create(name=username,
    #                             email=username+'@naturalis.nl',
    #                             password=pwd)
    #         uid = client.users.list(name=username)[0].id
    #         client.users.add_to_group(uid,sync_group_id)
    #         sendaccountmail(to_address,username,pwd)
    #         return True
    #     except Exception as e:
    #         log.logger.error('Unable to create user %s OR add it to group. Error: %s' % (username,e))
    #         return False
    #
    # def enable_user(client,username):
    #     """
    #     enables user in keystone. Takes:
    #     * keystone client object
    #     * username
    #     Returns True is succeeded, false if issues.
    #     """
    #
    #     try:
    #         uid = client.users.list(name=username)[0].id
    #         client.users.update(uid,enabled=True)
    #         return True
    #     except Exception as e:
    #         log.logger.error('Unable to enable user %s. Error: %s' % (username,e))
    #         return False
    #
    # def disable_user(client,username):
    #     """
    #     disables user in keystone. Takes:
    #     * keystone client object
    #     * username
    #     Returns True is succeeded, false if issues.
    #     """
    #     try:
    #         desc = "disabled_at:%s" % time.strftime("%d.%m.%Y")
    #         uid = client.users.list(name=username)[0].id
    #         client.users.update(uid,enabled=False,description=desc)
    #         return True
    #     except Exception as e:
    #         log.logger.error('Unable to disable user %s. Error: %s' % (username,e))
    #         return False
    #
    # def create_group(client,groupname):
    #     """
    #     Creates group in keystone. Takes:
    #     * keystone client object
    #     * groupname
    #     Returns True is succeeded, false if issues.
    #     """
    #     try:
    #         client.groups.create(name=groupname)
    #         return True
    #     except Exception as e:
    #         log.logger.error('Unable to create group %s. Error: %s' % (groupname,e))
    #         return False
    #
    # def delete_group(client,groupname):
    #     """
    #     Deletes group in keystone. Takes:
    #     * keystone client object
    #     * groupname
    #     Returns True is succeeded, false if issues.
    #     """
    #     try:
    #         gid = client.groups.list(name=groupname)[0].id
    #         gobj = client.groups.delete(gid)
    #         return True
    #     except Exception as e:
    #         log.logger.error('Unable to delete group %s. Error: %s' % (groupname,e))
    #         return False
    #
    # def add_user_to_group(client,groupname,username):
    #     """
    #     Adds user to group in keystone, Takes:
    #     * keystone client object
    #     * groupname
    #     * username
    #     Returns True if succeeded, false if issues
    #     """
    #     try:
    #         gid = client.groups.list(name=groupname)[0].id
    #         uid = client.users.list(name=username)[0].id
    #         client.users.add_to_group(uid,gid)
    #         return True
    #     except Exception as e:
    #         log.logger.error('Unable to add %s group %s. Error: %s' % (username,groupname,e))
    #         return False
    #
    # def remove_user_from_group(client,groupname,username):
    #     """
    #     Remove user to group in keystone, Takes:
    #     * keystone client object
    #     * groupname
    #     * username
    #     Returns True if succeeded, false if issues
    #     """
    #     try:
    #         gid = client.groups.list(name=groupname)[0].id
    #         uid = client.users.list(name=username)[0].id
    #         client.users.remove_from_group(uid,gid)
    #         return True
    #     except Exception as e:
    #         log.logger.error('Unable to remove %s group %s. Error: %s' % (username,groupname,e))
    #         return False
    #
    # def sendaccountmail(to,username,password):
    #     """
    #     Send an email to a email adress which contains
    #     the username and pass of the created user. Takes:
    #     * email address to send to
    #     * username
    #     * password
    #     """
    #     text = "An stack.naturalis.nl account has been created for:\n username: %s\n password: %s" % (username,password)
    #     msg = MIMEText(text)
    #     msg['Subject'] = 'stack.naturalis.nl account has been created for %s' % username
    #     msg['From'] = 'noreply@naturalis.nl'
    #     msg['To'] = to
    #
    #     s = smtplib.SMTP('aspmx.l.google.com')
    #     s.sendmail('noreply@naturalis.nl',[to],msg.as_string())
    #     s.quit()
