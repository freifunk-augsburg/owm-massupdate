from dns import resolver,reversename

def rresolv(ip):
    """Do a reverse DNS lookup for an IP address

    Args:
        * ip (string): IP address to do the reverse dns lookup for

    Returns:
        * String containing the PTR record or False if the lookup failed
    """

    try:
        addr=reversename.from_address(str(ip))
        rdns = str(resolver.query(addr,"PTR")[0])[:-1]
    except:
        rdns = False
    return rdns

