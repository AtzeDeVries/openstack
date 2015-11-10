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

    def update_access_to_project(self,project_name,group_names):
        """
        Update access to project
        : param str project_name: name of the project
        : param array group_names: array of the groups which should have access
        """
        excludes = ['SNB']
        # check if gives groupnames excist
        current_names = [ g.name for g in self.grouplist]
        to_be_deleted = []
        for gn in  group_names:
            if gn not in current_names:
                log.logger.warning("'%s' is not an excisting group" % gn)
                to_be_deleted.append(gn)

        for d in to_be_deleted:
            group_names.remove(d)

        current_access = []
        current_denied = []
        project_id = self.ksclient.projects.list(name=project_name)[0].id
        # implementation of check access in roles.py is very strange. If user has
        # no acccess it throws an error instead of false...
        for g in self.grouplist:
            if g.name in excludes:
                next
            try:
                access = self.ksclient.roles.check(self.member_role_id,group=g.id,project=project_id)
                current_access.append(g.name)
            except:
                log.logger.debug("Assuming that group '%s' has no access to '%s'" % (g.name,project_name))

        added = [a for a in group_names if (a not in current_access and a not in excludes)]
        removed = [ r for r in current_access if (r not in group_names and r not in excludes) ]

        log.logger.debug("'%s' will be added to project: '%s'" % (added,project_name))
        log.logger.debug("'%s' will be removed from project: '%s'" % (removed,project_name))

        for a in added:
            grp_id = self.ksclient.groups.list(name=a)[0].id
            log.logger.info("Granting access of %s to %s" % (a,project_name))
            self.ksclient.roles.grant(self.member_role_id,group=grp_id,project=project_id)

        for r in removed:
            grp_id = self.ksclient.groups.list(name=r)[0].id
            log.logger.info("Revoking access of %s to %s" % (r,project_name))
            self.ksclient.roles.revoke(self.member_role_id,group=grp_id,project=project_id)

    def check_if_project_excists(self,project_name):
        """
        Checks if projects (tenant) excists.
        : param str project_name: name of project
        Returns True or False
        """
        return len(self.ksclient.projects.list(name=project_name)) > 0

    def project_id_to_name(self,projectid):
        """
        Returns the name of the project when id is given
        : param str projectid: id of the project
        """
        return self.ksclient.projects.get(projectid).name

    def project_name_to_id(self,projectname):
        """
        Returns the id of the project when project name is given
        : param str projectname: name of the project
        """
        return self.ksclient.projects.list(name=projectname)[0].id
