"""
HTTP Server with Database Controller
Serves a simple web application with database connectivity
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from db_controller import DatabaseController


class SimpleServer(BaseHTTPRequestHandler):
    """HTTP Request handler with database controller integration"""
    
    db_controller = DatabaseController()
    
    def _set_headers(self, status_code=200, content_type="text/html"):
        """Set response headers"""
        self.send_response(status_code)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        # Base Route (Step 5 validation)
        if self.path == "/":
            self._set_headers()
            html_content = """
            <html>
                <body>
                    <h1>Web App Container Ready</h1>
                    <p>Go to <a href="/time">/time</a> to query the database.</p>
                </body>
            </html>
            """
            self.wfile.write(bytes(html_content, "utf-8"))
            
        # Time Endpoint (Step 7)
        elif self.path == "/time":
            response_data = self.db_controller.get_current_timestamp()
            
            if response_data["status"] == "success":
                self._set_headers(status_code=200, content_type="application/json")
            else:
                self._set_headers(status_code=500, content_type="application/json")
            
            self.wfile.write(bytes(json.dumps(response_data), "utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(bytes("404 Not Found", "utf-8"))


def run(server_class=HTTPServer, handler_class=SimpleServer, port=8080):
    """Start the HTTP server"""
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Server executing on port {port}...")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
