#!/usr/bin/env python3
"""
Renderbase Python SDK Integration Tests

Run these tests against a live API to verify SDK functionality.

Prerequisites:
1. Set RENDERBASE_API_KEY environment variable
2. Set RENDERBASE_API_URL environment variable (optional, defaults to https://api.renderbase.dev)
3. Have at least one template created in your workspace

Usage:
    RENDERBASE_API_KEY=your_key python tests/integration_test.py

Or with custom API URL:
    RENDERBASE_API_KEY=your_key RENDERBASE_API_URL=http://localhost:3000 python tests/integration_test.py
"""

import os
import sys
from typing import Optional, List, Tuple

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from renderbase import Renderbase, RenderbaseError

# Configuration
API_KEY = os.environ.get("RENDERBASE_API_KEY")
API_URL = os.environ.get("RENDERBASE_API_URL", "https://api.renderbase.dev")

if not API_KEY:
    print("❌ RENDERBASE_API_KEY environment variable is required")
    sys.exit(1)

client = Renderbase(
    api_key=API_KEY,
    base_url=API_URL,
)

# Test state
template_id: Optional[str] = None
template_variables: dict = {}
job_id: Optional[str] = None
webhook_id: Optional[str] = None

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
    global template_id, template_variables, job_id, webhook_id

    print("\n🧪 Renderbase Python SDK Integration Tests\n")
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
    # Webhooks Tests
    # ==========================================

    @test("webhooks.list() - List webhooks")
    def test_webhooks_list():
        response = client.webhooks.list()
        data = response.get("data", [])
        if not isinstance(data, list):
            raise Exception("Expected array of webhooks")
        print(f"  Found {len(data)} webhooks")

    test_webhooks_list()

    @test("webhooks.create() - Create webhook subscription")
    def test_webhooks_create():
        global webhook_id
        webhook = client.webhooks.create(
            url="https://webhook.site/test-renderbase-python-sdk",
            events=["document.generated", "document.failed"],
            description="SDK Integration Test Webhook (Python)",
        )

        if not webhook.get("id") or not webhook.get("secret"):
            raise Exception("Invalid webhook response")

        webhook_id = webhook["id"]
        print(f"  Webhook ID: {webhook_id}")
        print(f"  Secret: {webhook['secret'][:10]}...")

    test_webhooks_create()

    if webhook_id:
        @test("webhooks.get() - Get webhook by ID")
        def test_webhooks_get():
            webhook = client.webhooks.get(webhook_id)
            if not webhook.get("id") or not webhook.get("url"):
                raise Exception("Invalid webhook response")
            print(f"  URL: {webhook['url']}")

        test_webhooks_get()

        @test("webhooks.update() - Update webhook")
        def test_webhooks_update():
            webhook = client.webhooks.update(
                webhook_id,
                description="SDK Integration Test Webhook (Python - Updated)",
            )
            if not webhook.get("id"):
                raise Exception("Invalid webhook response")
            print(f"  Updated description: {webhook.get('description')}")

        test_webhooks_update()

        @test("webhooks.delete() - Delete webhook")
        def test_webhooks_delete():
            client.webhooks.delete(webhook_id)
            print(f"  Deleted webhook: {webhook_id}")

        test_webhooks_delete()

    # ==========================================
    # Error Handling Tests
    # ==========================================

    @test("Error handling - Invalid template ID")
    def test_error_handling():
        try:
            client.templates.get("invalid-template-id-12345")
            raise Exception("Expected error for invalid template")
        except RenderbaseError as e:
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
