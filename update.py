import sys
sys.path.insert(1, "./lib")
import json
import functions
from config import *
from owmdns import rresolv
from couch import Couch
import log
import argparse


# Parse arguments
parser = argparse.ArgumentParser(description='owm-massupdate help.')
parser.add_argument('-d', action='store_true', help='Delete nodes from map which are not online right now.')
parser.add_argument('-u', action='store_true', help='Update/create all nodes which are visible in your mesh right now.')
parser.add_argument('-q', action='store_true', help='Quiet, no output')
parser.add_argument('-v', action='store_true', help='Verbose output')
args = parser.parse_args()


logger = log.initialize_logging("owm-massupdate", args.q, args.v)


# Get data from olsr (latlon file and jsoninfo)
jsontbl = functions.get_jsoninfo(jsoninfosrc, 9090, 'topology')
if not jsontbl:
    logger.error("Error: Could not serialize the jsoninfo output")
    exit()

midtbl = functions.get_jsoninfo(jsoninfosrc, 9090, 'mid')
if not midtbl:
    logger.error("Error: Could not serialize the jsoninfo output")
    exit()

latlon = functions.getLatLon("/var/run/latlon.js")
latlon = functions.getNodes(latlon)

# initialize couch wrapper functions
db = Couch(couchserver, couchport)

# Get all nodes within boundingbox
nodes_on_map = db.listDoc('_spatial/nodes_essentials', 'bbox=10.571250915527344,48.306947615160205,11.226654052734375,48.43535105606878')['rows']

def get_node(hostname):
    etag = False
    r = db.openDoc(couchdb, hostname)
    try:
        etag = r['_rev']
    except KeyError:
        etag = False
    return r, etag

hosts = {}

for k in jsontbl:
    dest = rresolv(k['destinationIP'])
    lastHop = rresolv(k['lastHopIP'])
    # owm uses hostname.suffix as id. So no dns name, no update
    if not dest:
        logger.warn("Name resolution failed for " + k['destinationIP'])
    elif not lastHop:
        logger.warn("Name resolution failed for " + k['lastHopIP'])
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

if args.u:
    count_update = 0
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
            logger.info('Entry for ' + h + ' already exists, update it.')
            data = dict(recent_data.items() + data.items())
        else:
            logger.info('Creating entry for ' + h)


        data = json.dumps(data)

        logger.debug("Data sent: " + data)
        count_update = count_update + 1
        save = db.saveDoc(couchdb, data, h, etag)
        logger.debug("Data received" + json.dumps(save))

    logger.info("Updated: " + str(count_update))


if args.d:
    # Delete all entries which we did not update in this run
    count_delete = 0
    for n in nodes_on_map:
        hostname = n['id']
        if not hostname in hosts:
            node = db.openDoc(couchdb, hostname)
            etag = node['_rev']
            logger.info('Delete ' + hostname + ' from map.')
            delete = db.deleteDoc(couchdb, hostname, etag)
            logger.debug('Answer from couchdb: ' + delete)
            count_delete = count_delete +1
    logger.info("Deleted: " + str(count_delete))




