#!/usr/bin/env python3
"""
Rynko Python SDK Flow Integration Tests

Run these tests against a live API to verify Flow resource functionality.

Prerequisites:
1. Set RYNKO_API_KEY environment variable
2. Set RYNKO_API_URL environment variable (optional, defaults to https://api.rynko.dev)
3. Have at least one published Flow gate in your environment

Usage:
    RYNKO_API_KEY=your_key python tests/test_flow_integration.py

Or with custom API URL:
    RYNKO_API_KEY=your_key RYNKO_API_URL=http://localhost:3000 python tests/test_flow_integration.py
"""

import os
import sys
from typing import Optional, List, Tuple

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rynko import Rynko, RynkoError

# Configuration
API_KEY = os.environ.get("RYNKO_API_KEY")
API_URL = os.environ.get("RYNKO_API_URL", "https://api.rynko.dev")

if not API_KEY:
    print("❌ RYNKO_API_KEY environment variable is required")
    sys.exit(1)

client = Rynko(
    api_key=API_KEY,
    base_url=API_URL,
)

# Test state
gate_id: Optional[str] = None
run_id: Optional[str] = None
approval_id: Optional[str] = None
delivery_id: Optional[str] = None

# Test results tracking
results: List[Tuple[str, bool, Optional[str]]] = []


def test(name: str):
    """Decorator for test functions"""
    def decorator(fn):
        def wrapper(*args, **kwargs):
            try:
                fn(*args, **kwargs)
                results.append((name, True, None))
                print(f"✅ {name}")
            except Exception as e:
                results.append((name, False, str(e)))
                print(f"❌ {name}: {e}")
        return wrapper
    return decorator


def run_tests():
    global gate_id, run_id, approval_id, delivery_id

    print("\n🧪 Rynko Python SDK Flow Integration Tests\n")
    print(f"API URL: {API_URL}")
    print(f"API Key: {API_KEY[:10]}...")
    print("\n---\n")

    # ==========================================
    # Gates Tests (read-only)
    # ==========================================

    @test("flow.list_gates() - List all gates")
    def test_list_gates():
        global gate_id
        response = client.flow.list_gates()
        data = response.get("data", [])
        meta = response.get("meta", {})
        if not isinstance(data, list):
            raise Exception("Expected array of gates")
        if "total" not in meta:
            raise Exception("Expected meta.total in response")
        print(f"  Found {len(data)} gates (total: {meta['total']})")

        # Save first published gate ID for later tests
        for gate in data:
            if gate.get("status") == "published":
                gate_id = gate["id"]
                print(f"  Using gate: {gate['name']} ({gate_id})")
                break

        if not gate_id and len(data) > 0:
            gate_id = data[0]["id"]
            print(f"  Using gate: {data[0].get('name')} ({gate_id})")

    test_list_gates()

    if gate_id:
        @test("flow.get_gate() - Get gate by ID")
        def test_get_gate():
            gate = client.flow.get_gate(gate_id)
            if not gate.get("id"):
                raise Exception("Invalid gate response - missing id")
            if not gate.get("name"):
                raise Exception("Invalid gate response - missing name")
            print(f"  Gate: {gate['name']}")
            print(f"  Status: {gate.get('status')}")

        test_get_gate()

    # ==========================================
    # Runs Tests
    # ==========================================

    if gate_id:
        @test("flow.submit_run() - Submit a run to a gate")
        def test_submit_run():
            global run_id
            run = client.flow.submit_run(
                gate_id,
                input={
                    "name": "Integration Test",
                    "amount": 42.00,
                    "email": "test@example.com",
                },
                metadata={
                    "source": "sdk-python-integration-test",
                    "testRun": True,
                },
            )

            if not run.get("id"):
                raise Exception("Invalid run response - missing id")
            if not run.get("status"):
                raise Exception("Invalid run response - missing status")

            run_id = run["id"]
            print(f"  Run ID: {run_id}")
            print(f"  Status: {run['status']}")

        test_submit_run()

    if run_id:
        @test("flow.get_run() - Get run by ID")
        def test_get_run():
            run = client.flow.get_run(run_id)
            if not run.get("id"):
                raise Exception("Invalid run response - missing id")
            if not run.get("status"):
                raise Exception("Invalid run response - missing status")
            print(f"  Status: {run['status']}")
            if run.get("errors"):
                print(f"  Errors: {len(run['errors'])}")

        test_get_run()

    @test("flow.list_runs() - List all runs")
    def test_list_runs():
        response = client.flow.list_runs(limit=10)
        data = response.get("data", [])
        meta = response.get("meta", {})
        if not isinstance(data, list):
            raise Exception("Expected array of runs")
        if "total" not in meta:
            raise Exception("Expected meta.total in response")
        print(f"  Found {len(data)} runs (total: {meta['total']})")

    test_list_runs()

    if gate_id:
        @test("flow.list_runs_by_gate() - List runs for a specific gate")
        def test_list_runs_by_gate():
            response = client.flow.list_runs_by_gate(gate_id, limit=10)
            data = response.get("data", [])
            meta = response.get("meta", {})
            if not isinstance(data, list):
                raise Exception("Expected array of runs")
            if "total" not in meta:
                raise Exception("Expected meta.total in response")
            print(f"  Found {len(data)} runs for gate {gate_id}")

        test_list_runs_by_gate()

    @test("flow.list_active_runs() - List active runs")
    def test_list_active_runs():
        response = client.flow.list_active_runs(limit=10)
        data = response.get("data", [])
        meta = response.get("meta", {})
        if not isinstance(data, list):
            raise Exception("Expected array of runs")
        if "total" not in meta:
            raise Exception("Expected meta.total in response")
        print(f"  Found {len(data)} active runs")

    test_list_active_runs()

    if run_id:
        @test("flow.wait_for_run() - Wait for run to complete")
        def test_wait_for_run():
            completed = client.flow.wait_for_run(
                run_id,
                poll_interval=1.0,
                timeout=60.0,
            )

            terminal = {
                "completed", "delivered", "approved", "rejected",
                "validation_failed", "render_failed", "delivery_failed",
            }
            if completed["status"] not in terminal:
                raise Exception(f"Run not finished: {completed['status']}")

            print(f"  Final status: {completed['status']}")
            if completed.get("output"):
                print(f"  Output keys: {list(completed['output'].keys())}")
            if completed.get("errors"):
                print(f"  Errors: {len(completed['errors'])}")

        test_wait_for_run()

    # ==========================================
    # Approvals Tests
    # ==========================================

    @test("flow.list_approvals() - List all approvals")
    def test_list_approvals():
        global approval_id
        response = client.flow.list_approvals(limit=10)
        data = response.get("data", [])
        meta = response.get("meta", {})
        if not isinstance(data, list):
            raise Exception("Expected array of approvals")
        if "total" not in meta:
            raise Exception("Expected meta.total in response")
        print(f"  Found {len(data)} approvals (total: {meta['total']})")

        # Save first pending approval ID for later tests
        for appr in data:
            if appr.get("status") == "pending":
                approval_id = appr["id"]
                print(f"  Found pending approval: {approval_id}")
                break

    test_list_approvals()

    @test("flow.approve() - Approve a pending approval")
    def test_approve():
        if not approval_id:
            print("  Skipped: no pending approvals")
            return

        result = client.flow.approve(approval_id, note="Approved via SDK integration test")
        if not result.get("id"):
            raise Exception("Invalid approval response")
        print(f"  Approved: {result['id']}")
        print(f"  Status: {result.get('status')}")

    test_approve()

    @test("flow.reject() - Reject a pending approval")
    def test_reject():
        # Look for another pending approval
        response = client.flow.list_approvals(status="pending", limit=1)
        pending = response.get("data", [])
        if not pending:
            print("  Skipped: no pending approvals")
            return

        reject_id = pending[0]["id"]
        result = client.flow.reject(reject_id, reason="Rejected via SDK integration test")
        if not result.get("id"):
            raise Exception("Invalid rejection response")
        print(f"  Rejected: {result['id']}")
        print(f"  Status: {result.get('status')}")

    test_reject()

    # ==========================================
    # Deliveries Tests
    # ==========================================

    if run_id:
        @test("flow.list_deliveries() - List deliveries for a run")
        def test_list_deliveries():
            global delivery_id
            response = client.flow.list_deliveries(run_id, limit=10)
            data = response.get("data", [])
            meta = response.get("meta", {})
            if not isinstance(data, list):
                raise Exception("Expected array of deliveries")
            if "total" not in meta:
                raise Exception("Expected meta.total in response")
            print(f"  Found {len(data)} deliveries for run {run_id}")

            # Save first failed delivery ID for retry test
            for d in data:
                if d.get("status") == "failed":
                    delivery_id = d["id"]
                    print(f"  Found failed delivery: {delivery_id}")
                    break

        test_list_deliveries()

    @test("flow.retry_delivery() - Retry a failed delivery")
    def test_retry_delivery():
        if not delivery_id:
            print("  Skipped: no failed deliveries")
            return

        result = client.flow.retry_delivery(delivery_id)
        if not result.get("id"):
            raise Exception("Invalid retry response")
        print(f"  Retried: {result['id']}")
        print(f"  Status: {result.get('status')}")

    test_retry_delivery()

    # ==========================================
    # Error Handling Tests
    # ==========================================

    @test("Error handling - Invalid run ID")
    def test_error_handling():
        try:
            client.flow.get_run("invalid-run-id-12345")
            raise Exception("Expected error for invalid run ID")
        except RynkoError as e:
            print(f"  Error code: {e.code}")
            print(f"  Status: {e.status_code}")
            return  # Test passed
        except Exception:
            raise

    test_error_handling()

    # ==========================================
    # Results Summary
    # ==========================================

    print("\n---\n")
    print("📊 Test Results Summary\n")

    passed = sum(1 for r in results if r[1])
    failed = sum(1 for r in results if not r[1])

    print(f"Total: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed > 0:
        print("\n❌ Failed Tests:")
        for name, success, error in results:
            if not success:
                print(f"  - {name}: {error}")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")


if __name__ == "__main__":
    run_tests()
