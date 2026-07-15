#!/usr/bin/env python3
"""
Dummy WMS app + e2e: calls the Rynko Reporting API with an API key via the SDK,
over real HTTP.

By default it spins a local mock API (so it runs anywhere) and asserts the SDK's
authenticated calls + response parsing. Point it at a real server with:
    RYNKO_API_KEY=... RYNKO_API_URL=https://api.rynko.dev python examples/reporting_e2e.py
"""

import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_KEY = os.environ.get("RYNKO_API_KEY", "test-api-key")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # silence
        pass

    def _auth_ok(self) -> bool:
        return self.headers.get("Authorization") == f"Bearer {API_KEY}"

    def _send(self, code, obj):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode())

    def do_GET(self):
        if not self._auth_ok():
            return self._send(401, {"message": "unauthorized"})
        if self.path.startswith("/api/reporting/run-link/reports"):
            return self._send(200, {"reports": [{"id": "r1", "slug": "daily", "name": "Daily"}]})
        self._send(404, {"message": "not found", "path": self.path})

    def do_POST(self):
        if not self._auth_ok():
            return self._send(401, {"message": "unauthorized"})
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        if self.path == "/api/reporting/run-link/mint":
            return self._send(200, {
                "token": "rrt_x",
                "url": f"https://app.rynko.dev/run/{body.get('reportRef', '')}?t=rrt_x",
                "expiresAt": "2026-07-15T10:15:00Z",
                "mode": "report" if body.get("reportRef") else "landing",
            })
        if self.path == "/api/reporting/run-link/run-direct":
            return self._send(200, {"runId": "run_x", "status": "pending"})
        self._send(404, {"message": "not found", "path": self.path})


def main():
    base = os.environ.get("RYNKO_API_URL")
    using_mock = base is None
    server = None
    if using_mock:
        server = HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_address[1]}"

    print(f"Reporting SDK e2e against {'mock' if using_mock else 'live'} API: {base}")

    from rynko import Rynko

    client = Rynko(api_key=API_KEY, base_url=base)

    reports = client.reporting.list_reports()
    print("list_reports ->", len(reports), "report(s)")
    if using_mock:
        assert len(reports) == 1 and reports[0]["slug"] == "daily", "list_reports parse"
    report_ref = reports[0]["slug"] if reports else "daily"

    link = client.reporting.mint_run_link(
        report_ref=report_ref,
        locked_params={"warehouse": "W1"},
        actor={"externalUserId": "jdoe", "name": "Jane Doe"},
        ttl_minutes=15,
    )
    print("mint_run_link ->", link["url"])
    if using_mock:
        assert link["token"] == "rrt_x" and report_ref in link["url"], "mint parse"

    run = client.reporting.run_report(report_ref, params={"date": "2026-07-15"})
    print("run_report ->", run["runId"], run["status"])
    if using_mock:
        assert run["runId"] == "run_x", "run_report parse"

    if server:
        server.shutdown()
    print("✓ reporting SDK e2e passed")


if __name__ == "__main__":
    main()
