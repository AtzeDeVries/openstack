from keystoneclient.auth.identity import v2
from keystoneclient import session
from novaclient import client
from . import log

allowed_types = ['ha_localdisk','hpc','ha_ceph']


class Nova():

    def __init__(self,auth_url,username,password,tenant_name):
        auth = v2.Password(auth_url=auth_url,
                           username=username,
                           password=password,
                           tenant_name=tenant_name)
        sess = session.Session(auth=auth,verify='./stack_naturalis_nl.ca-bundle')
        self.nova = client.Client("2",session=sess)


    def flavor_access(self,flavor):
        return self.__get_flavor_access_list(flavor)

    def grant_to_flavor(self,flavorname,projectid):
        try:
            flid = self.__get_flavor_id(flavorname)
            self.nova.flavor_access.add_tenant_access(flid,projectid)
            return True
        except Exception as e:
            log.logger.debug(e)
            return False


    def update_quota(self,project_id,items):
        print __quota_compare(project_id,items)
        # current = self.__list_quota(project_id)
        # new = {}
        # if items['cpu'] != current.cores:
        #     new.update({'cores': items['cpu']})
        # if items['ram'] != current.ram:
        #     new.update({'ram': items['ram']})
        # if items['floatingips'] != current.floating_ips:
        #     new.update({'floating_ips' : items['floating_ips']})
        # if items['instances'] != current.instances:
        #     new.update({'instances': items['instances']})
        # if items['securitygroups'] != current.security_groups:

#< instances=100, key_pairs=10, metadata_items=1024, ram=51200, security_group_rules=20, security_groups=10, server_group_members=10, server_groups=10>

    def __quota_compare(self,project_id,items):
        current = self.__list_quota(project_id)
        new = {}
        for key,value in items.iteritems():
            try:
                if value != getattr(current,value):
                    new.update({key: value})
            except Exception as e:
                log.waring("Could not parse quota of project %s with quota setting %s" % (project_id,key))
        return new

    def __list_quota(self,project_id):
        return self.nova.quotas.get(project_id)

    def revoke_to_flavor(self,flavorname,projectid):
        try:
            flid = self.__get_flavor_id(flavorname)
            self.nova.flavor_access.remove_tenant_access(flid,projectid)
            return True
        except Exception as e:
            log.logger.debug(e)
            return False

    def __get_flavor_access_list(self,flavor):
        flid = self.__get_flavor_id(flavor)
        if not flid:
            raise NameError("Flavor %s does not exist" % flavor)
        else:
            return self.nova.flavor_access._list_by_flavor(flid)

    def __get_flavor_id(self,flavor):
        all_flavors = self.nova.flavors.list()
        exists = False
        for f in all_flavors:
            if f.name == flavor:
                exists = f.id
                break
        return exists








#sess = session.Session(auth=auth,verify='cert/stack_naturalis_nl.ca-bundle')
