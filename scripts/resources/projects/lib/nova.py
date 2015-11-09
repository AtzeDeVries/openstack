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


    def show(self,flavor):
        return self.__get_flavor_access_list(flavor)

    def __get_flavor_access_list(self,flavor):
        flid = self.__get_flavor_id(flavor)
        if not flid:
            log.logger.warning("Flavor %s does not exist" % flavor)
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
