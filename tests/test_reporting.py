#!/usr/bin/env python3
"""
Reporting Resource unit tests (mocked HTTP — no live API).
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rynko import Rynko
from rynko.resources.reporting import ReportingResource


class FakeHttp:
    def __init__(self, result=None):
        self.calls = []
        self.result = result if result is not None else {}

    def post(self, path, body=None):
        self.calls.append(("POST", path, body))
        return self.result

    def get(self, path, params=None):
        self.calls.append(("GET", path, params))
        return self.result


class TestReporting(unittest.TestCase):
    def test_mint_run_link(self):
        http = FakeHttp({"token": "rrt_x", "url": "u", "expiresAt": "e", "mode": "report"})
        res = ReportingResource(http).mint_run_link(
            report_ref="daily-progress",
            locked_params={"warehouse": "W1"},
            actor={"externalUserId": "jdoe", "name": "Jane"},
            ttl_minutes=15,
        )
        self.assertEqual(
            http.calls[0],
            (
                "POST",
                "/api/reporting/run-link/mint",
                {
                    "reportRef": "daily-progress",
                    "lockedParams": {"warehouse": "W1"},
                    "actor": {"externalUserId": "jdoe", "name": "Jane"},
                    "ttlMinutes": 15,
                },
            ),
        )
        self.assertEqual(res["token"], "rrt_x")

    def test_mint_landing_omits_report_ref(self):
        http = FakeHttp()
        ReportingResource(http).mint_run_link()
        self.assertEqual(http.calls[0][2], {})

    def test_run_report(self):
        http = FakeHttp({"runId": "run_x", "status": "pending"})
        res = ReportingResource(http).run_report(
            "daily-progress", params={"date": "2026-07-15"}
        )
        self.assertEqual(
            http.calls[0],
            (
                "POST",
                "/api/reporting/run-link/run-direct",
                {"reportRef": "daily-progress", "params": {"date": "2026-07-15"}},
            ),
        )
        self.assertEqual(res["runId"], "run_x")

    def test_list_reports(self):
        http = FakeHttp({"reports": [{"id": "r1", "slug": "daily", "name": "Daily"}]})
        reports = ReportingResource(http).list_reports()
        self.assertEqual(http.calls[0], ("GET", "/api/reporting/run-link/reports", None))
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0]["id"], "r1")

    def test_list_reports_empty(self):
        self.assertEqual(ReportingResource(FakeHttp({})).list_reports(), [])

    def test_client_exposes_reporting(self):
        client = Rynko(api_key="test-key")
        self.assertIsInstance(client.reporting, ReportingResource)


if __name__ == "__main__":
    unittest.main()
