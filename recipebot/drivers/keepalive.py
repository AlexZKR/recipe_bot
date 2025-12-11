import base64
import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from recipebot.config import settings

logger = logging.getLogger(__name__)


class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/metrics":
            if self._check_auth():
                self.send_response(200)
                self.send_header("Content-Type", CONTENT_TYPE_LATEST)
                self.end_headers()
                self.wfile.write(generate_latest())
            else:
                self.send_response(401)
                self.send_header("WWW-Authenticate", 'Basic realm="Metrics"')
                self.end_headers()
                self.wfile.write(b"Authentication required")
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is running!")

    def _check_auth(self) -> bool:
        """Validates Basic Auth header."""
        auth_header = self.headers.get("Authorization")
        if not auth_header:
            return False

        try:
            scheme, params = auth_header.split()
            if scheme.lower() != "basic":
                return False

            decoded = base64.b64decode(params).decode("utf-8")
            username, password = decoded.split(":")

            return (
                username == settings.APP.metrics_user
                and password == settings.APP.metrics_pass.get_secret_value()
            )
        except Exception:
            return False


def start_health_check():
    port = int(os.environ.get("PORT", "8080"))
    logger.info(f"Starting health check server on port {port}")

    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)  # nosec B104
    server.serve_forever()
