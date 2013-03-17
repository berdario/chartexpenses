#! /usr/bin/env python3

from csv import reader
from http.server import HTTPServer, BaseHTTPRequestHandler
from json import dumps
from sys import argv
from os import path
import webbrowser

PORT = 9000

def csv_to_json():
    spese = []
    with open(argv[1], encoding="utf-8") as f:
        for line in reader(f):
            spese.extend((line[0], desc, cost, name or "all") for desc,cost,name in zip(filter(None, line[2::3]), line[3::3], line[4::3]))

    return dumps([("date", "desc", "cost", "name")] + spese).encode()

class JsonHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'jsonp(' + csv_to_json() + b')')
        return


url = "file://" + path.join(path.dirname(path.abspath(__file__)), "afterquery", "render.html") + "#url=http://localhost:{0}{{}}&title={1}".format(PORT, path.basename(argv[1]))

webbrowser.open(url.format("&treegroup=name,desc;cost&chart=tree"))
webbrowser.open(url.format("&pivot=date;name;cost&chart=stacked"))

httpd = HTTPServer(('', PORT), JsonHandler)
httpd.serve_forever()
