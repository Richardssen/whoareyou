import optparse
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

@app.route('/whois/<path:domain>')
def whois_domain(domain):
	privatedomain = tldextract.extract(domain)
	try:
		response = pythonwhois.get_whois(str(privatedomain.registered_domain))
	except Exception, e:
		response = dict()
		response['err'] = str(e) 
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
