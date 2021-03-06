#from keystoneclient.auth.identity import v2
#from keystoneclient import session
from neutronclient.v2_0 import client
from . import log



class Neutron():

    def __init__(self,auth_url,username,password,tenant_name,ca_cert):
        # auth = v2.Password(auth_url=auth_url,
        #                    username=username,
        #                    password=password,
        #                    tenant_name=tenant_name)
        # sess = session.Session(auth=auth,verify='./stack_naturalis_nl.ca-bundle')
        self.neutron = client.Client(username=username,password=password,
                                     tenant_name=tenant_name,auth_url=auth_url,
                                     ca_cert=ca_cert)


    def update_quota(self,project_id,items):
        new = self.__quota_compare(project_id,items)
        if new != {}:
            try:
                log.logger.info("Trying to update quota of %s with %s" % (project_id,new))
                self.neutron.update_quota(project_id,{'quota':new})
            except Exception as e:
                log.logger.warning("Failed to update quota of %s with %s" % (project_id,new))
                log.logger.debug(e)
        else:
            log.logger.debug("No need to update neutron quota of %s" % project_id)

    def create_default_network(self, project_id, gateway_id, dns_servers = ['8.8.8.8','8.8.4.4']):
        state = [self.__router_exists(project_id), self.__network_exists(project_id), self.__subnet_exists(project_id)]
        if not any(state):
            try:
                log.logger.info("Creating a network for %s" % project_id)
                new_router = self.neutron.create_router(body={'router': {'tenant_id': project_id , 'admin_state_up': True ,'name' : 'router', 'distributed': True} })['router']['id']
                self.neutron.add_gateway_router(new_router, body={"network_id": gateway_id})
                new_network = self.neutron.create_network(body={'network': {'tenant_id': project_id, 'name': 'network'}})['network']['id']
                new_subnet = self.neutron.create_subnet(body={'subnet':{'tenant_id':project_id,
                                                                        'name':'subnet',
                                                                        'ip_version': 4,
                                                                        'network_id': new_network,
                                                                        'cidr': '172.16.1.0/24',
                                                                        'dns_nameservers':dns_servers}})['subnet']['id']
                self.neutron.add_interface_router(new_router,{'subnet_id': new_subnet})
            except Exception as e:
                log.logger.warning(e)

        else:
            log.logger.debug("No network creating neccecary for %s" % project_id)

    def __router_exists(self,project_id):
        _params = {'tenant_id' : project_id }
        return len(self.neutron.list_routers(retrieve_all=True,**_params)['routers']) > 0

    def __network_exists(self,project_id):
        _params = {'tenant_id' : project_id }
        return len(self.neutron.list_networks(retrieve_all=True,**_params)['networks']) > 0

    def __subnet_exists(self,project_id):
        _params = {'tenant_id' : project_id }
        return len(self.neutron.list_subnets(retrieve_all=True,**_params)['subnets']) > 0

    def __list_quota(self,project_id):
        return self.neutron.show_quota(project_id)['quota']


    def __quota_compare(self,project_id,items):
        current = self.__list_quota(project_id)
        new = {}
        for key,value in items.iteritems():
            try:
                if value != current[key]:
                #if value != getattr(current,key):
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
