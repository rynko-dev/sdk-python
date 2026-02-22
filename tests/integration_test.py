#!/usr/bin/env python3
"""
Rynko Python SDK Integration Tests

Run these tests against a live API to verify SDK functionality.

Prerequisites:
1. Set RYNKO_API_KEY environment variable
2. Set RYNKO_API_URL environment variable (optional, defaults to https://api.rynko.dev)
3. Have at least one template created in your environment

Usage:
    RYNKO_API_KEY=your_key python tests/integration_test.py

Or with custom API URL:
    RYNKO_API_KEY=your_key RYNKO_API_URL=http://localhost:3000 python tests/integration_test.py
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
template_id: Optional[str] = None
template_variables: dict = {}
job_id: Optional[str] = None

# Test results tracking
results: List[Tuple[str, bool, Optional[str]]] = []


def build_variables_from_defaults(variables: list) -> dict:
    """Build variables object from template variable definitions using default values"""
    result = {}

    if not variables or not isinstance(variables, list):
        return result

    for variable in variables:
        if variable.get("name") and variable.get("defaultValue") is not None:
            result[variable["name"]] = variable["defaultValue"]

    return result


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
    global template_id, template_variables, job_id

    print("\n🧪 Rynko Python SDK Integration Tests\n")
    print(f"API URL: {API_URL}")
    print(f"API Key: {API_KEY[:10]}...")
    print("\n---\n")

    # ==========================================
    # Client Tests
    # ==========================================

    @test("client.me() - Get authenticated user")
    def test_me():
        user = client.me()
        if not user.get("id") or not user.get("email"):
            raise Exception("Invalid user response")
        print(f"  User: {user['email']}")

    test_me()

    @test("client.verify_api_key() - Verify API key is valid")
    def test_verify_api_key():
        result = client.verify_api_key()
        if not result:
            raise Exception("API key verification failed")

    test_verify_api_key()

    # ==========================================
    # Templates Tests
    # ==========================================

    @test("templates.list() - List all templates")
    def test_templates_list():
        global template_id
        response = client.templates.list()
        data = response.get("data", [])
        if not isinstance(data, list):
            raise Exception("Expected array of templates")
        print(f"  Found {len(data)} templates")

        # Save first template ID for later tests
        if len(data) > 0:
            template_id = data[0]["id"]
            print(f"  Using template: {data[0]['name']} ({template_id})")

    test_templates_list()

    @test("templates.list_pdf() - Filter PDF templates")
    def test_templates_list_filtered():
        response = client.templates.list_pdf()
        data = response.get("data", [])
        if not isinstance(data, list):
            raise Exception("Expected array of templates")
        print(f"  Found {len(data)} PDF templates")

    test_templates_list_filtered()

    if template_id:
        @test("templates.get() - Get template by ID")
        def test_templates_get():
            global template_variables
            template = client.templates.get(template_id)
            if not template.get("id") or not template.get("name"):
                raise Exception("Invalid template response")
            print(f"  Template: {template['name']}")
            print(f"  Variables: {len(template.get('variables', []))}")

            # Extract default values from template variables
            template_variables = build_variables_from_defaults(template.get("variables", []))
            print(f"  Using {len(template_variables)} variables with defaults")

        test_templates_get()

    # ==========================================
    # Documents Tests
    # ==========================================

    if template_id:
        @test("documents.generate_pdf() - Generate PDF document")
        def test_generate_pdf():
            global job_id
            job = client.documents.generate_pdf(
                template_id=template_id,
                variables=template_variables,
            )

            if not job.get("jobId") or job.get("status") != "queued":
                raise Exception("Invalid job response")

            job_id = job["jobId"]
            print(f"  Job ID: {job_id}")
            print(f"  Status: {job['status']}")

        test_generate_pdf()

        if job_id:
            @test("documents.get_job() - Get job status")
            def test_get_job():
                job = client.documents.get_job(job_id)
                if not job.get("jobId"):
                    raise Exception("Invalid job response")
                print(f"  Status: {job['status']}")

            test_get_job()

            @test("documents.wait_for_completion() - Wait for job completion")
            def test_wait_for_completion():
                completed = client.documents.wait_for_completion(
                    job_id,
                    poll_interval=1.0,
                    timeout=60.0,
                )

                if completed["status"] not in ["completed", "failed"]:
                    raise Exception(f"Job not finished: {completed['status']}")

                print(f"  Final status: {completed['status']}")
                if completed.get("downloadUrl"):
                    print(f"  Download URL: {completed['downloadUrl'][:50]}...")

            test_wait_for_completion()

        # --- PDF Generation with Metadata ---
        metadata_job_id = None
        test_metadata = {
            "orderId": "ord_test_12345",
            "customerId": "cust_test_67890",
            "priority": 1,
            "isTest": True,
        }

        @test("documents.generate_pdf() - Generate PDF with metadata")
        def test_generate_pdf_with_metadata():
            nonlocal metadata_job_id
            job = client.documents.generate_pdf(
                template_id=template_id,
                variables=template_variables,
                metadata=test_metadata,
            )

            if not job.get("jobId") or job.get("status") != "queued":
                raise Exception("Invalid job response")

            metadata_job_id = job["jobId"]
            print(f"  Job ID: {metadata_job_id}")
            print(f"  Status: {job['status']}")
            print(f"  Metadata sent: {test_metadata}")

        test_generate_pdf_with_metadata()

        if metadata_job_id:
            @test("documents.wait_for_completion() - Verify metadata in completed job")
            def test_verify_metadata():
                completed = client.documents.wait_for_completion(
                    metadata_job_id,
                    poll_interval=1.0,
                    timeout=60.0,
                )

                if completed["status"] not in ["completed", "failed"]:
                    raise Exception(f"Job not finished: {completed['status']}")

                print(f"  Final status: {completed['status']}")

                # Verify metadata is returned
                returned_metadata = completed.get("metadata")
                if not returned_metadata:
                    raise Exception("Metadata not returned in completed job")

                if returned_metadata.get("orderId") != test_metadata["orderId"]:
                    raise Exception(f"Metadata orderId mismatch: expected {test_metadata['orderId']}, got {returned_metadata.get('orderId')}")

                if returned_metadata.get("customerId") != test_metadata["customerId"]:
                    raise Exception(f"Metadata customerId mismatch: expected {test_metadata['customerId']}, got {returned_metadata.get('customerId')}")

                if returned_metadata.get("priority") != test_metadata["priority"]:
                    raise Exception(f"Metadata priority mismatch: expected {test_metadata['priority']}, got {returned_metadata.get('priority')}")

                print(f"  Metadata returned: {returned_metadata}")
                print(f"  ✓ All metadata fields verified")

            test_verify_metadata()

        # --- Excel Generation ---
        excel_job_id = None

        @test("documents.generate_excel() - Generate Excel document")
        def test_generate_excel():
            nonlocal excel_job_id
            job = client.documents.generate_excel(
                template_id=template_id,
                variables=template_variables,
            )

            if not job.get("jobId") or job.get("status") != "queued":
                raise Exception("Invalid job response")

            excel_job_id = job["jobId"]
            print(f"  Job ID: {excel_job_id}")
            print(f"  Status: {job['status']}")

        test_generate_excel()

        if excel_job_id:
            @test("documents.get_job() - Get Excel job status")
            def test_get_excel_job():
                job = client.documents.get_job(excel_job_id)
                if not job.get("jobId"):
                    raise Exception("Invalid job response")
                print(f"  Status: {job['status']}")

            test_get_excel_job()

            @test("documents.wait_for_completion() - Wait for Excel completion")
            def test_wait_for_excel_completion():
                completed = client.documents.wait_for_completion(
                    excel_job_id,
                    poll_interval=1.0,
                    timeout=60.0,
                )

                if completed["status"] not in ["completed", "failed"]:
                    raise Exception(f"Job not finished: {completed['status']}")

                print(f"  Final status: {completed['status']}")
                if completed.get("downloadUrl"):
                    print(f"  Download URL: {completed['downloadUrl'][:50]}...")

            test_wait_for_excel_completion()

        # --- List Jobs ---
        @test("documents.list_jobs() - List document jobs")
        def test_list_jobs():
            response = client.documents.list_jobs(limit=10)
            data = response.get("data", [])
            if not isinstance(data, list):
                raise Exception("Expected array of jobs")
            print(f"  Found {len(data)} jobs")

        test_list_jobs()

        @test("documents.list_jobs(status='completed') - Filter by status")
        def test_list_jobs_filtered():
            response = client.documents.list_jobs(status="completed", limit=5)
            data = response.get("data", [])
            if not isinstance(data, list):
                raise Exception("Expected array of jobs")
            print(f"  Found {len(data)} completed jobs")

        test_list_jobs_filtered()

    # ==========================================
    # Webhooks Tests (Read-only)
    # ==========================================

    @test("webhooks.list() - List webhooks")
    def test_webhooks_list():
        response = client.webhooks.list()
        data = response.get("data", [])
        if not isinstance(data, list):
            raise Exception("Expected array of webhooks")
        print(f"  Found {len(data)} webhooks")

        # If webhooks exist, test get by ID
        if len(data) > 0:
            webhook_id = data[0]["id"]
            webhook = client.webhooks.get(webhook_id)
            if not webhook.get("id") or not webhook.get("url"):
                raise Exception("Invalid webhook response")
            print(f"  Retrieved webhook: {webhook_id}")

    test_webhooks_list()

    # ==========================================
    # Error Handling Tests
    # ==========================================

    @test("Error handling - Invalid template ID")
    def test_error_handling():
        try:
            client.templates.get("invalid-template-id-12345")
            raise Exception("Expected error for invalid template")
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
