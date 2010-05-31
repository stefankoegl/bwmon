# -*- coding: utf-8 -*-

from __future__ import absolute_import

import BaseHTTPServer

import os

JS = open(os.path.join(os.path.dirname(__file__) or '.', '..', 'all.js')).read()

HTML = """
        <script type="text/javascript">
            window.onload = function() {
                var paper = new Raphael(0, 0, 640, 480);
                paper.g.linechart(0, 0, 640, 480, %s, %s);
            }
        </script>
    </head>
    <body>
    </body>
</html>
"""

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    monitor = None

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Refresh', '5')
        self.end_headers()

        x, yy = self.monitor.get_datapoints()

        self.wfile.write('<html><head><script type="text/javascript">')
        self.wfile.write(JS)
        self.wfile.write('</script>')
        self.wfile.write(HTML % (repr(x), repr(yy)))

#server = BaseHTTPServer.HTTPServer(('', 8000), RequestHandler)
#while True:
#    server.handle_request()

