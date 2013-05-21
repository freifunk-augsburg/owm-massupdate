import telnetlib
import re
import json


def get_jsoninfo(host, port, what):
    """ Get jsoninfo output from olsrd

    Args:
        * host = Hostname or IP address to connect to jsoninfo
        * port = port of jsoninfo
        * what = what you want to fetch, i.e. 'all', 'links' etc.

    Returns:
        Dictionary containing the requested info or False if we could not get
        any data.
    """

    try:
        tn = telnetlib.Telnet(host, port)
        tn.write("/" + what + "\n")
        raw = tn.read_all()
        tbl = json.loads(raw)
        print tbl
        return tbl[what]
    except:
        return False

def getLatLon(file):
    with open(file, 'r') as f:
        info = str(f.read())
        f.closed
        latlon = re.split('\n', info)
    return latlon

def getNodes(latlon):
    latlondict = {}

    for n in latlon:
        if n.startswith('Node') or n.startswith('Self'):
            #Node('10.11.0.20',48.357758,10.886595,0,'10.11.4.42','openlab-indoor');
            data = re.search(".*\((.*).*\);", n).group(1).replace('\'', '')
            data = data.split(',')
            latlondict[data[0]] = { 'lat': data[1], 'lon': data[2] }
    return latlondict

