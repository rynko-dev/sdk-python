#!/usr/bin/env python3
"""
Flow Types Unit Tests

Tests for Flow type definitions and constants.
These tests don't require a live API.
"""

import unittest

from rynko import (
    FlowRunStatus,
    FLOW_RUN_TERMINAL_STATUSES,
    FlowGate,
    FlowRun,
    FlowValidationError,
    FlowApproval,
    FlowDelivery,
    SubmitRunOptions,
    ListGatesOptions,
    ListRunsOptions,
    ListApprovalsOptions,
)


class TestFlowRunStatus(unittest.TestCase):
    """Tests for FlowRunStatus literal type."""

    def test_pending_is_valid_status(self):
        """pending should be a valid FlowRunStatus."""
        status: FlowRunStatus = "pending"
        self.assertEqual(status, "pending")

    def test_validating_is_valid_status(self):
        """validating should be a valid FlowRunStatus."""
        status: FlowRunStatus = "validating"
        self.assertEqual(status, "validating")

    def test_approved_is_valid_status(self):
        """approved should be a valid FlowRunStatus."""
        status: FlowRunStatus = "approved"
        self.assertEqual(status, "approved")

    def test_rejected_is_valid_status(self):
        """rejected should be a valid FlowRunStatus."""
        status: FlowRunStatus = "rejected"
        self.assertEqual(status, "rejected")

    def test_all_statuses_are_strings(self):
        """All FlowRunStatus values should be strings."""
        statuses = [
            "pending",
            "validating",
            "approved",
            "rejected",
            "review_required",
            "completed",
            "delivered",
            "validation_failed",
            "render_failed",
            "delivery_failed",
        ]
        for s in statuses:
            self.assertIsInstance(s, str)


class TestFlowRunTerminalStatuses(unittest.TestCase):
    """Tests for FLOW_RUN_TERMINAL_STATUSES frozenset."""

    def test_is_frozenset(self):
        """FLOW_RUN_TERMINAL_STATUSES should be a frozenset."""
        self.assertIsInstance(FLOW_RUN_TERMINAL_STATUSES, frozenset)

    def test_approved_is_terminal(self):
        """approved should be a terminal status."""
        self.assertIn("approved", FLOW_RUN_TERMINAL_STATUSES)

    def test_rejected_is_terminal(self):
        """rejected should be a terminal status."""
        self.assertIn("rejected", FLOW_RUN_TERMINAL_STATUSES)

    def test_completed_is_terminal(self):
        """completed should be a terminal status."""
        self.assertIn("completed", FLOW_RUN_TERMINAL_STATUSES)

    def test_delivered_is_terminal(self):
        """delivered should be a terminal status."""
        self.assertIn("delivered", FLOW_RUN_TERMINAL_STATUSES)

    def test_validation_failed_is_terminal(self):
        """validation_failed should be a terminal status."""
        self.assertIn("validation_failed", FLOW_RUN_TERMINAL_STATUSES)

    def test_render_failed_is_terminal(self):
        """render_failed should be a terminal status."""
        self.assertIn("render_failed", FLOW_RUN_TERMINAL_STATUSES)

    def test_delivery_failed_is_terminal(self):
        """delivery_failed should be a terminal status."""
        self.assertIn("delivery_failed", FLOW_RUN_TERMINAL_STATUSES)

    def test_pending_is_not_terminal(self):
        """pending should NOT be a terminal status."""
        self.assertNotIn("pending", FLOW_RUN_TERMINAL_STATUSES)

    def test_validating_is_not_terminal(self):
        """validating should NOT be a terminal status."""
        self.assertNotIn("validating", FLOW_RUN_TERMINAL_STATUSES)

    def test_review_required_is_not_terminal(self):
        """review_required should NOT be a terminal status."""
        self.assertNotIn("review_required", FLOW_RUN_TERMINAL_STATUSES)


class TestFlowGateShape(unittest.TestCase):
    """Tests for FlowGate TypedDict shape."""

    def test_gate_has_required_fields(self):
        """FlowGate should accept all expected fields."""
        gate: FlowGate = {
            "id": "gate_abc123",
            "name": "Invoice Validator",
            "slug": "invoice-validator",
            "description": "Validates invoice data",
            "status": "published",
            "schema_version": 1,
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        }
        self.assertEqual(gate["id"], "gate_abc123")
        self.assertEqual(gate["name"], "Invoice Validator")
        self.assertEqual(gate["status"], "published")

    def test_gate_optional_fields(self):
        """FlowGate should work with only partial fields."""
        gate: FlowGate = {
            "id": "gate_abc123",
            "name": "My Gate",
            "status": "draft",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        }
        self.assertNotIn("slug", gate)
        self.assertNotIn("description", gate)


class TestFlowRunShape(unittest.TestCase):
    """Tests for FlowRun TypedDict shape."""

    def test_run_has_expected_fields(self):
        """FlowRun should accept all expected fields."""
        run: FlowRun = {
            "id": "run_abc123",
            "gate_id": "gate_def456",
            "status": "approved",
            "input": {"name": "John Doe", "amount": 150.00},
            "output": {"normalized_name": "JOHN DOE"},
            "errors": None,
            "metadata": {"source": "checkout"},
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "completed_at": "2026-01-01T00:01:00Z",
        }
        self.assertEqual(run["id"], "run_abc123")
        self.assertEqual(run["gate_id"], "gate_def456")
        self.assertEqual(run["status"], "approved")
        self.assertIsInstance(run["input"], dict)

    def test_run_with_errors(self):
        """FlowRun should accept a list of validation errors."""
        run: FlowRun = {
            "id": "run_abc123",
            "gate_id": "gate_def456",
            "status": "rejected",
            "input": {"amount": -5},
            "errors": [
                {"field": "amount", "rule": "min", "message": "Must be positive"},
            ],
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        }
        self.assertEqual(len(run["errors"]), 1)
        self.assertEqual(run["errors"][0]["field"], "amount")


class TestFlowValidationErrorShape(unittest.TestCase):
    """Tests for FlowValidationError TypedDict shape."""

    def test_validation_error_full(self):
        """FlowValidationError should accept all fields."""
        error: FlowValidationError = {
            "field": "email",
            "rule": "format",
            "message": "Invalid email format",
        }
        self.assertEqual(error["field"], "email")
        self.assertEqual(error["rule"], "format")
        self.assertEqual(error["message"], "Invalid email format")

    def test_validation_error_message_only(self):
        """FlowValidationError should work with only message."""
        error: FlowValidationError = {
            "message": "General validation failure",
        }
        self.assertEqual(error["message"], "General validation failure")
        self.assertNotIn("field", error)
        self.assertNotIn("rule", error)


class TestFlowApprovalShape(unittest.TestCase):
    """Tests for FlowApproval TypedDict shape."""

    def test_approval_has_expected_fields(self):
        """FlowApproval should accept all expected fields."""
        approval: FlowApproval = {
            "id": "appr_abc123",
            "run_id": "run_def456",
            "gate_id": "gate_ghi789",
            "status": "pending",
            "reviewer_email": "reviewer@example.com",
            "reviewer_note": None,
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "resolved_at": None,
        }
        self.assertEqual(approval["id"], "appr_abc123")
        self.assertEqual(approval["run_id"], "run_def456")
        self.assertEqual(approval["status"], "pending")
        self.assertIsNone(approval["resolved_at"])

    def test_approval_resolved(self):
        """FlowApproval should accept resolved state."""
        approval: FlowApproval = {
            "id": "appr_abc123",
            "run_id": "run_def456",
            "gate_id": "gate_ghi789",
            "status": "approved",
            "reviewer_note": "Looks good",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "resolved_at": "2026-01-01T00:05:00Z",
        }
        self.assertEqual(approval["status"], "approved")
        self.assertEqual(approval["reviewer_note"], "Looks good")
        self.assertIsNotNone(approval["resolved_at"])


class TestFlowDeliveryShape(unittest.TestCase):
    """Tests for FlowDelivery TypedDict shape."""

    def test_delivery_has_expected_fields(self):
        """FlowDelivery should accept all expected fields."""
        delivery: FlowDelivery = {
            "id": "del_abc123",
            "run_id": "run_def456",
            "status": "delivered",
            "url": "https://example.com/webhook",
            "http_status": 200,
            "attempts": 1,
            "last_attempt_at": "2026-01-01T00:01:00Z",
            "error": None,
            "created_at": "2026-01-01T00:00:00Z",
        }
        self.assertEqual(delivery["id"], "del_abc123")
        self.assertEqual(delivery["status"], "delivered")
        self.assertEqual(delivery["http_status"], 200)
        self.assertEqual(delivery["attempts"], 1)

    def test_delivery_failed(self):
        """FlowDelivery should accept failed state with error."""
        delivery: FlowDelivery = {
            "id": "del_abc123",
            "run_id": "run_def456",
            "status": "failed",
            "url": "https://example.com/webhook",
            "http_status": 500,
            "attempts": 3,
            "last_attempt_at": "2026-01-01T00:05:00Z",
            "error": "Connection refused",
            "created_at": "2026-01-01T00:00:00Z",
        }
        self.assertEqual(delivery["status"], "failed")
        self.assertEqual(delivery["error"], "Connection refused")
        self.assertEqual(delivery["attempts"], 3)


class TestSubmitRunOptionsShape(unittest.TestCase):
    """Tests for SubmitRunOptions TypedDict shape."""

    def test_submit_run_options_full(self):
        """SubmitRunOptions should accept all fields."""
        options: SubmitRunOptions = {
            "input": {"name": "John", "amount": 100},
            "metadata": {"source": "api"},
            "webhook_url": "https://example.com/hook",
        }
        self.assertIsInstance(options["input"], dict)
        self.assertEqual(options["metadata"]["source"], "api")
        self.assertEqual(options["webhook_url"], "https://example.com/hook")

    def test_submit_run_options_minimal(self):
        """SubmitRunOptions should work with only input."""
        options: SubmitRunOptions = {
            "input": {"name": "Jane"},
        }
        self.assertIn("input", options)
        self.assertNotIn("metadata", options)
        self.assertNotIn("webhook_url", options)


class TestListOptionsShapes(unittest.TestCase):
    """Tests for list option TypedDict shapes."""

    def test_list_gates_options(self):
        """ListGatesOptions should accept filter fields."""
        options: ListGatesOptions = {
            "status": "published",
            "limit": 50,
            "page": 2,
        }
        self.assertEqual(options["status"], "published")
        self.assertEqual(options["limit"], 50)
        self.assertEqual(options["page"], 2)

    def test_list_runs_options(self):
        """ListRunsOptions should accept filter fields."""
        options: ListRunsOptions = {
            "status": "approved",
            "limit": 10,
            "page": 1,
        }
        self.assertEqual(options["status"], "approved")
        self.assertEqual(options["limit"], 10)

    def test_list_approvals_options(self):
        """ListApprovalsOptions should accept filter fields."""
        options: ListApprovalsOptions = {
            "status": "pending",
            "limit": 25,
            "page": 1,
        }
        self.assertEqual(options["status"], "pending")
        self.assertEqual(options["limit"], 25)

    def test_list_options_empty(self):
        """List options should work with no fields."""
        gates_opts: ListGatesOptions = {}
        runs_opts: ListRunsOptions = {}
        approvals_opts: ListApprovalsOptions = {}
        self.assertEqual(len(gates_opts), 0)
        self.assertEqual(len(runs_opts), 0)
        self.assertEqual(len(approvals_opts), 0)


if __name__ == "__main__":
    unittest.main()
