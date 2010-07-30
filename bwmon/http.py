# -*- coding: utf-8 -*-
#
# Copyright 2010 Thomas Perl and Stefan Kögl. All rights reserved.
#
# Developed for a practical course (Large-scaled distributed computing) at the
# University of Technology Vienna in the 2010 summer term.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHORS ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

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
    """HTTP Request handler (returns monitoring data)

    This is a simple request handler used by the built-in
    HTTP server to visualize the monitoring data.
    """
    monitor = None

    def do_GET(self):
        """Handler for HTTP GET requests
        """
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

