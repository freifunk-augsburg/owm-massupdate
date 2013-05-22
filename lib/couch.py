#! /usr/bin/python2.6

import httplib, json

def prettyPrint(s):
    """Prettyprints the json response of an HTTPResponse object"""

    # HTTPResponse instance -> Python object -> str
    print json.dumps(json.loads(s.read()), sort_keys=True, indent=4)

class Couch:
    """Basic wrapper class for operations on a couchDB"""

    def __init__(self, host, port=5984, options=None):
        self.host = host
        self.port = port

    def connect(self):
        return httplib.HTTPConnection(self.host, self.port) # No close()

    # Document operations

    def listDoc(self, dbName, query=None):
        """List all documents in a given database"""

        if query:
            r = self.get(''.join(['/', dbName, '/', '?', query]))
        else:
            r = self.get(''.join(['/', dbName, '/', '_all_docs']))
        return json.loads(r.read())

    def openDoc(self, dbName, docId):
        """Open a document in a given database"""
        r = self.get(''.join(['/', dbName, '/', docId,]))
        return json.loads(r.read())

    def saveDoc(self, dbName, body, docId=None, rev=False):
        """Save/create a document to/in a given database"""
        if docId:
            if rev:
                r = self.put(''.join(['/', dbName, '/', docId, '?rev=', rev]), str(body))
            else:
                r = self.put(''.join(['/', dbName, '/', docId]), str(body))
        else:
            if rev:
                r = self.post(''.join(['/', dbName, '/', '?rev=', rev]), str(body))
            else:
                r = self.post(''.join(['/', dbName, '/']), str(body))

        return json.loads(r.read())

    def deleteDoc(self, dbName, docId, rev):
        r = self.delete(''.join(['/', dbName, '/', docId, '?rev=', rev]))
        return json.loads(r.read())

    # Basic http methods

    def get(self, uri):
        c = self.connect()
        headers = {"Accept": "application/json"}
        c.request("GET", uri, None, headers)
        return c.getresponse()

    def post(self, uri, body):
        c = self.connect()
        headers = {"Content-type": "application/json"}
        c.request('POST', uri, body, headers)
        return c.getresponse()

    def put(self, uri, body):
        c = self.connect()
        if len(body) > 0:
            headers = {"Content-type": "application/json"}
            c.request("PUT", uri, body, headers)
        else:
            c.request("PUT", uri, body)
        return c.getresponse()

    def delete(self, uri):
        c = self.connect()
        c.request("DELETE", uri)
        return c.getresponse()

