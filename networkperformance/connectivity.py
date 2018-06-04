import socket

try:
    from urllib2 import urlopen, URLError
    from urlparse import urlparse
except ImportError:  # Python 3
    from urllib.parse import urlparse
    from urllib.request import urlopen, URLError


class Connectivity(object):

    conn_url = 'https://www.google.com/'

    def __init__(self):
        pass

    def hasinternet(self):
        try:
            data = urlopen(self.conn_url, timeout=5)
        except URLError:
            print ("No internet access.")
            return False

        try:
            host = data.fp._sock.fp._sock.getpeername()
        except AttributeError:  # Python 3
            host = data.fp.raw._sock.getpeername()

        # Ensure conn_url is an IPv4 address otherwise future queries will fail
        self.conn_url = 'http://' + (host[0] if len(host) == 2 else
                                     socket.gethostbyname(urlparse(data.geturl()).hostname))

        return True
