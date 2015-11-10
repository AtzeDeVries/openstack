from keystoneclient.auth.identity import v2
from keystoneclient import session
from cinderclient import client
from . import log



class Cinder():

    def __init__(self,auth_url,username,password,tenant_name):
        auth = v2.Password(auth_url=auth_url,
                           username=username,
                           password=password,
                           tenant_name=tenant_name)
        sess = session.Session(auth=auth,verify='./stack_naturalis_nl.ca-bundle')
        self.cinder = client.Client("2",session=sess)

    def list(self):
        print self.cinder.volumes.list()

    def update_quota(self,project_id,items):
        return self.__quota_compare(project_id,items)

    def __get_quota(self,project_id):
        print self.cinder.quotas.get(project_id)
        return self.cinder.quotas.get(project_id)['quota_set']

    def __quota_compare(self,project_id,items):
        current = self.__get_quota(project_id)
        print current
        new = {}
        for key,value in items.iteritems():
            try:
                if value != current[key]:
                    new.update({key: value})
            except Exception as e:
                log.logger.warning("Could not parse quota of project %s with quota setting %s" % (project_id,key))
        return new


    # def flavor_access(self,flavor):
    #     return self.__get_flavor_access_list(flavor)
    #
    # def grant_to_flavor(self,flavorname,projectid):
    #     try:
    #         flid = self.__get_flavor_id(flavorname)
    #         self.nova.flavor_access.add_tenant_access(flid,projectid)
    #         return True
    #     except Exception as e:
    #         log.logger.debug(e)
    #         return False
    #
    #
    # def update_quota(self,project_id,items):
    #     kwargs = self.__quota_compare(project_id,items)
    #     if kwargs != {}:
    #         kwargs.update({"tenant_id": project_id})
    #         try:
    #             self.nova.quotas.update(**kwargs)
    #             log.logger.debug("trying to update project_id: %s with quota: %s" % (project_id,kwargs))
    #             return True
    #         except Exception as e:
    #             log.logger.debug(e)
    #             return False
    #     else:
    #         return None
    #
    #
    # def __quota_compare(self,project_id,items):
    #     current = self.__list_quota(project_id)
    #     new = {}
    #     for key,value in items.iteritems():
    #         try:
    #             if value != getattr(current,key):
    #                 new.update({key: value})
    #         except Exception as e:
    #             log.logger.warning("Could not parse quota of project %s with quota setting %s" % (project_id,key))
    #     return new
    #
    # def __list_quota(self,project_id):
    #     return self.nova.quotas.get(project_id)
    #
    # def revoke_to_flavor(self,flavorname,projectid):
    #     try:
    #         flid = self.__get_flavor_id(flavorname)
    #         self.nova.flavor_access.remove_tenant_access(flid,projectid)
    #         return True
    #     except Exception as e:
    #         log.logger.debug(e)
    #         return False
    #
    # def __get_flavor_access_list(self,flavor):
    #     flid = self.__get_flavor_id(flavor)
    #     if not flid:
    #         raise NameError("Flavor %s does not exist" % flavor)
    #     else:
    #         return self.nova.flavor_access._list_by_flavor(flid)
    #
    # def __get_flavor_id(self,flavor):
    #     all_flavors = self.nova.flavors.list()
    #     exists = False
    #     for f in all_flavors:
    #         if f.name == flavor:
    #             exists = f.id
    #             break
    #     return exists
    #
    #






#sess = session.Session(auth=auth,verify='cert/stack_naturalis_nl.ca-bundle')
