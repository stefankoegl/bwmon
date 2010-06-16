
import sys
import urllib2
import socket

socket.setdefaulttimeout(1)

RANDOM_URL = 'http://random.yahoo.com/bin/ryl'
COUNT = 200

urls = []
while len(urls) < COUNT:
    try:
        fp = urllib2.urlopen(RANDOM_URL)
        print fp.url
        urls.append(fp.url)
        fp.close()
        sys.stdout.flush()
    except Exception, e:
        print >>sys.stderr, e
        continue

