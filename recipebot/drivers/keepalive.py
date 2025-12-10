import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

logger = logging.getLogger(__name__)


class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")


def start_health_check():
    port = int(os.environ.get("PORT", "8080"))
    logger.info(f"Starting health check server on port {port}")

    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)  # nosec B104
    server.serve_forever()
