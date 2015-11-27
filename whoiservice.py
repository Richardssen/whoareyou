#!/usr/bin/env python
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

__author__ = "ffranz"
__copyright__ = "2015"
__credits__ = ["ffranz"]
__license__ = "GPL"
__version__ = "0.0.2"
__maintainer__ = "ffranz"
__email__ = "ffranz@sinfonier-project.net"
__status__ = "Developing"


import optparse
import socket, re, sys
import pythonwhois
import tldextract
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def hide_service():
	abort(404)

@app.route('/about')
def about():
	return 'WHOIS (pronounced as the phrase who is) is a query and response protocol that is widely used for querying databases that store the registered users or assignees of an Internet resource, such as a domain name, an IP address block, or an autonomous system, but is also used for a wider range of other information. The protocol stores and delivers database content in a human-readable format.[1] The WHOIS protocol is documented in RFC 3912.'

@app.route('/whois/domain/<path:domain>')
@app.route('/whois/<path:domain>')
def whois_domain(domain):
	privatedomain = tldextract.extract(domain)
	try:
		response = pythonwhois.get_whois(str(privatedomain.registered_domain))
	except Exception, e:
		response = dict()
		response['err'] = str(e) 
	return jsonify(response)

@app.route('/whois/ip/<path:ip>')
def whois_ip(ip):
	try:
		obj = IPWhois(str(ip))
		response = obj.lookup_rdap(depth=1)
		print response
	except Exception, e:
		response = dict()
		response['err'] = str(e)
	return jsonify(response)

@app.route('/whois/recursive/<path:server>/<path:port>/<path:ip>')
def whois_recursive(ip, server, port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((server, int(port)))
	query = "-r -a -c -m -B "+ip
	sock.send(("%s\r\n" % query).encode("utf-8"))
	buff = b""
	while True:
		data = sock.recv(1024)
		if len(data) == 0:
			break
		buff += data
	result = buff.decode("utf-8")
	reslist = list()
	resdict = dict()
	for i in result.split("\n"):
		if not i.startswith('%'):
			if i.strip() != '':
				if ( "net6num" in i or "route6" in i ) and bool(resdict):
					reslist.append(resdict)
					resdict = dict()
				key = i.split(':')[0].strip()
				value = i.split(key+":")[1].strip()
				line = dict()
				line[key] = value
				resdict.update(line)
	response = dict()
	response["ipaddress"] = ip
	response["server"] = server
	response["port"] = port
	response["response"] = reslist
	return jsonify(response)

def main():
    parser = optparse.OptionParser(usage="%prog [options]  or type %prog -h (--help)")
    parser.add_option('-p','--port',
		dest='port',
		action='store',
		help='The port to run server on',
		default=4343)
    (options, args) = parser.parse_args()
    port = int(options.port)
    print 'Tornado on port {port}...'.format(port=port)

    from tornado.wsgi import WSGIContainer
    from tornado.httpserver import HTTPServer
    from tornado.ioloop import IOLoop

    http_server = HTTPServer(WSGIContainer(app))

    http_server.listen(int(port))
    IOLoop.instance().start()

if __name__ == '__main__':
	main()
