from ldap3 import Server, Connection, ALL
from . import log
def connect(host,u,p):
    """Setup LDAP to Host. Takes arguments
    * host (ip/dns of domain controller)
    * username with domain in DOMAIN\\Username writing
    * password of user
    returns connection object"""

    s = Server(host,
               get_info=ALL)
    c = Connection(s,
                   user=u,
                   password=p,
                   read_only=True)
    return c
