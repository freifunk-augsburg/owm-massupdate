import sys
sys.path.insert(1, "./lib")
import json
import functions
from dns import resolver,reversename
from couch import Couch

# variables - adapt to your settings here

couchserver = 'openwifimap.net'
couchport = '80'
couchdb = 'openwifimap'
jsoninfosrc = '192.168.2.1'

# End variables


# Get data from olsr (latlon file and jsoninfo)
jsontbl = functions.get_jsoninfo(jsoninfosrc, 9090, 'topology')
if not jsontbl:
    print("Error: Could not serialize the jsoninfo output")
    exit()

midtbl = functions.get_jsoninfo(jsoninfosrc, 9090, 'mid')
if not midtbl:
    print("Error: Could not serialize the jsoninfo output")
    exit()

latlon = functions.getLatLon("/var/run/latlon.js")
latlon = functions.getNodes(latlon)

# initialize couch wrapper functions
db = Couch(couchserver, couchport)

def get_node(hostname):
    etag = False
    r = db.openDoc(couchdb, hostname)
    try:
        etag = r['_rev']
    except KeyError:
        etag = False
    return r, etag

def rresolv(ip):
    try:
        addr=reversename.from_address(str(ip))
        rdns = str(resolver.query(addr,"PTR")[0])[:-1]
    except:
        rdns = False
    return rdns

hosts = {}

for k in jsontbl:
    dest = rresolv(k['destinationIP'])
    lastHop = rresolv(k['lastHopIP'])
    # owm uses hostname.suffix as id. So no dns name, no update
    if not dest:
        print("Name resolution failed for " + k['destinationIP'])
    elif not lastHop:
        print("Name resolution failed for " + k['lastHopIP'])
    else:
        try:
            lat = latlon[k['destinationIP']]['lat']
        except KeyError:
            lat = '0.0'

        try:
            lon = latlon[k['destinationIP']]['lon']
        except KeyError:
            lon = '0.0'

        if not dest in hosts:
            hosts[dest] = { 'lat': lat, 'lon': lon, 'links': [{ 'id': lastHop, 'quality': float(k['linkQuality'])}]}
        else:
            hosts[dest]['links'].append({ 'id': lastHop, 'quality': float(k['linkQuality'])})

for h in hosts:
    recent_data, etag = get_node(h)

    data = {
        "_id": h,
        "type": "node",
        "hostname": h,
        "latitude": float(hosts[h]['lat']),
        "longitude": float(hosts[h]['lon']),
        "updateInterval": 60,
        "links": hosts[h]['links']
    }

    if etag: # entry exists, skip it
        print('Entry for ' + h + ' already exists, update it.')
	data = dict(recent_data.items() + data.items())
    else:
        print('Creating entry for ' + h)

    db.saveDoc(couchdb, data, h, etag)


