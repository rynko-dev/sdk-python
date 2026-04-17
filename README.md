# rynko

Official Python SDK for [Rynko](https://rynko.dev) - the document generation and AI output validation platform with unified template design for PDF and Excel documents.

[![PyPI version](https://img.shields.io/pypi/v/rynko.svg)](https://pypi.org/project/rynko/)
[![Python versions](https://img.shields.io/pypi/pyversions/rynko.svg)](https://pypi.org/project/rynko/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Features](#features)
- [Authentication](#authentication)
- [Document Generation](#document-generation)
  - [Generate PDF](#generate-pdf)
  - [Generate Excel](#generate-excel)
  - [Generate with Options](#generate-with-options)
  - [Batch Generation](#batch-generation)
  - [Wait for Completion](#wait-for-completion)
- [Document Jobs](#document-jobs)
  - [Get Job Status](#get-job-status)
  - [List Jobs](#list-jobs)
  - [Delete Job](#delete-job)
  - [Retry Job](#retry-job)
  - [Cancel Job](#cancel-job)
  - [Batch Status](#batch-status)
  - [Download Document](#download-document)
- [Templates](#templates)
  - [List Templates](#list-templates)
  - [Get Template Details](#get-template-details)
- [Webhooks](#webhooks)
  - [List Webhooks](#list-webhooks)
  - [Create Webhook](#create-webhook)
  - [Update Webhook](#update-webhook)
  - [Delete Webhook](#delete-webhook)
  - [Rotate Secret](#rotate-secret)
  - [Test Webhook](#test-webhook)
  - [Webhook Deliveries](#webhook-deliveries)
  - [Verify Webhook Signatures](#verify-webhook-signatures)
- [Rynko Flow](#rynko-flow)
  - [Submit and Wait for Run](#submit-and-wait-for-run)
  - [List Gates](#list-gates)
  - [Gate Management](#gate-management)
  - [Test and Validate](#test-and-validate)
  - [Manage Approvals](#manage-approvals)
  - [Monitor Deliveries](#monitor-deliveries)
  - [Run Payloads and Chains](#run-payloads-and-chains)
- [Rynko Extract](#rynko-extract)
  - [Create Extraction Job](#create-extraction-job)
  - [Schema Discovery](#schema-discovery)
  - [Extraction Configs](#extraction-configs)
  - [Flow Integration](#flow-integration)
- [Async Client](#async-client)
- [Configuration](#configuration)
- [Error Handling](#error-handling)
- [Context Manager](#context-manager)
- [API Reference](#api-reference)
- [Requirements](#requirements)
- [Support](#support)

## Installation

```bash
pip install rynko
```

The async client (`AsyncRynko`) is included by default — no extra dependencies needed, since `httpx` provides built-in async support.

## Quick Start

```python
from rynko import Rynko

client = Rynko(api_key="your_api_key")

# Generate a PDF document (async - returns job info immediately)
job = client.documents.generate_pdf(
    template_id="tmpl_invoice",
    variables={
        "customerName": "John Doe",
        "invoiceNumber": "INV-001",
        "total": 150.00,
    },
)

print(f"Job ID: {job['jobId']}")
print(f"Status: {job['status']}")  # 'queued'

# Wait for completion to get the download URL
completed = client.documents.wait_for_completion(job["jobId"])
print(f"Download URL: {completed['downloadUrl']}")
```

## Features

- **Sync and async clients** - Choose based on your application needs
- **Full type hints** - Complete type annotation support for IDE autocompletion
- **PDF generation** - Generate PDF documents from templates
- **Excel generation** - Generate Excel spreadsheets from templates
- **Batch generation** - Generate multiple documents in a single request
- **Environment support** - Generate documents in specific environments
- **Webhook verification** - Secure HMAC signature verification for incoming webhooks
- **Polling utility** - Built-in `wait_for_completion()` method with configurable timeout
- **Rynko Flow** - Submit runs for validation, manage approvals, gate CRUD, and monitor deliveries
- **Rynko Extract** - Document data extraction with AI, schema discovery, and config management
- **Webhook management** - Full CRUD for webhook subscriptions, secret rotation, and delivery tracking
- **Context manager support** - Automatic resource cleanup

## Authentication

### Get an API Key

1. Log in to your [Rynko Dashboard](https://app.rynko.dev)
2. Navigate to **Settings** → **API Keys**
3. Click **Create API Key**
4. Copy the key and store it securely (it won't be shown again)

### Initialize the Client

```python
import os
from rynko import Rynko

# Using environment variable (recommended)
client = Rynko(api_key=os.environ["RYNKO_API_KEY"])

# Verify authentication
user = client.me()
print(f"Authenticated as: {user['email']}")
print(f"Project: {user.get('teamName')}")
```

### Verify API Key

```python
# Check if API key is valid
is_valid = client.verify_api_key()
print(f"API Key valid: {is_valid}")
```

## Document Generation

Document generation in Rynko is **asynchronous**. When you call a generate method, the job is queued for processing and you receive a job ID immediately. Use `wait_for_completion()` to poll until the document is ready.

### Generate PDF

```python
# Queue PDF generation
job = client.documents.generate_pdf(
    template_id="tmpl_invoice",
    variables={
        "invoiceNumber": "INV-001",
        "customerName": "John Doe",
        "customerEmail": "john@example.com",
        "items": [
            {"description": "Product A", "quantity": 2, "price": 50.00},
            {"description": "Product B", "quantity": 1, "price": 50.00},
        ],
        "subtotal": 150.00,
        "tax": 15.00,
        "total": 165.00,
    },
)

print(f"Job queued: {job['jobId']}")
print(f"Status: {job['status']}")  # 'queued'

# Wait for completion
completed = client.documents.wait_for_completion(job["jobId"])
print(f"Download URL: {completed['downloadUrl']}")
```

### Generate Excel

```python
job = client.documents.generate_excel(
    template_id="tmpl_sales_report",
    variables={
        "reportTitle": "Q1 2026 Sales Report",
        "reportDate": "2026-03-31",
        "salesData": [
            {"region": "North", "q1": 125000, "q2": 0, "q3": 0, "q4": 0},
            {"region": "South", "q1": 98000, "q2": 0, "q3": 0, "q4": 0},
            {"region": "East", "q1": 145000, "q2": 0, "q3": 0, "q4": 0},
            {"region": "West", "q1": 112000, "q2": 0, "q3": 0, "q4": 0},
        ],
        "totalSales": 480000,
    },
)

completed = client.documents.wait_for_completion(job["jobId"])
print(f"Excel file ready: {completed['downloadUrl']}")
```

### Generate with Options

The `generate()` method supports all document formats and advanced options:

```python
job = client.documents.generate(
    # Required
    template_id="tmpl_contract",
    format="pdf",  # 'pdf' | 'excel' | 'csv'

    # Template variables
    variables={
        "contractNumber": "CTR-2026-001",
        "clientName": "Acme Corporation",
        "startDate": "2026-02-01",
        "endDate": "2027-01-31",
    },

    # Optional settings
    filename="contract-acme-2026",  # Custom filename (without extension)
    webhook_url="https://your-app.com/webhooks/document-ready",  # Webhook notification
    metadata={                       # Custom metadata (passed to webhook)
        "orderId": "ORD-12345",
        "userId": "user_abc",
    },
    use_draft=False,                 # Use draft template version (for testing)
    use_credit=False,                # Force use of purchased credits
)
```

### Batch Generation

Generate multiple documents from a single template:

```python
# Each dict in the documents list requires a "variables" key
batch = client.documents.generate_batch(
    template_id="tmpl_invoice",
    format="pdf",
    documents=[
        {
            "variables": {
                "invoiceNumber": "INV-001",
                "customerName": "John Doe",
                "total": 150.00,
            },
        },
        {
            "variables": {
                "invoiceNumber": "INV-002",
                "customerName": "Jane Smith",
                "total": 275.50,
            },
        },
        {
            "variables": {
                "invoiceNumber": "INV-003",
                "customerName": "Bob Wilson",
                "total": 89.99,
            },
        },
    ],
    webhook_url="https://your-app.com/webhooks/batch-complete",
)

print(f"Batch ID: {batch['batchId']}")
print(f"Total jobs: {batch['totalJobs']}")  # 3
print(f"Status: {batch['status']}")  # 'queued'
print(f"Estimated wait: {batch['estimatedWaitSeconds']} seconds")
```

### Wait for Completion

The `wait_for_completion()` method polls the job status until it completes or fails:

```python
# Default settings (1 second interval, 30 second timeout)
completed = client.documents.wait_for_completion(job["jobId"])

# Custom polling settings
completed = client.documents.wait_for_completion(
    job["jobId"],
    poll_interval=2.0,   # Check every 2 seconds
    timeout=60.0,        # Wait up to 60 seconds
)

# Check result
if completed["status"] == "completed":
    print(f"Download URL: {completed['downloadUrl']}")
    print(f"File size: {completed['fileSize']} bytes")
    print(f"Expires at: {completed['downloadUrlExpiresAt']}")
elif completed["status"] == "failed":
    print(f"Generation failed: {completed['errorMessage']}")
    print(f"Error code: {completed['errorCode']}")
```

## Document Jobs

### Get Job Status

```python
job = client.documents.get_job("job_abc123")

print(f"Status: {job['status']}")
# Possible values: 'queued' | 'processing' | 'completed' | 'failed'

print(f"Template: {job.get('templateName')}")
print(f"Format: {job['format']}")
print(f"Created: {job['createdAt']}")

if job["status"] == "completed":
    print(f"Download URL: {job['downloadUrl']}")
    print(f"File size: {job['fileSize']}")
    print(f"URL expires: {job['downloadUrlExpiresAt']}")

if job["status"] == "failed":
    print(f"Error: {job['errorMessage']}")
    print(f"Error code: {job['errorCode']}")
```

### List Jobs

```python
# List recent jobs with pagination
result = client.documents.list_jobs(limit=20, page=1)
jobs = result["data"]
meta = result["meta"]

print(f"Total jobs: {meta['total']}")
print(f"Pages: {meta['totalPages']}")

for job in jobs:
    print(f"{job['jobId']}: {job['status']} - {job.get('templateName')}")

# Filter by status
result = client.documents.list_jobs(status="completed")

# Filter by template
result = client.documents.list_jobs(template_id="tmpl_invoice")

# Filter by environment
result = client.documents.list_jobs(workspace_id="ws_abc123")

# Combine filters
result = client.documents.list_jobs(
    status="completed",
    template_id="tmpl_invoice",
    limit=50,
)
```

### Delete Job

```python
client.documents.delete("job_abc123")
```

### Retry Job

```python
result = client.documents.retry("job_abc123")
print(f"New job: {result['jobId']}")
```

### Cancel Job

```python
client.documents.cancel("job_abc123")
```

### Batch Status

```python
# Get batch status
batch = client.documents.get_batch("batch_abc123")
print(f"Status: {batch['status']}")
print(f"Progress: {batch['completedJobs']}/{batch['totalJobs']}")

# Wait for batch to complete (polls until terminal state)
completed = client.documents.wait_for_batch_completion(
    "batch_abc123",
    poll_interval=2.0,   # Check every 2 seconds (default)
    timeout=300.0,        # Wait up to 5 minutes (default)
)
print(f"Final status: {completed['status']}")
```

### Download Document

```python
# Download the generated document as bytes
job = client.documents.wait_for_completion("job_abc123")
content = client.documents.download(job["downloadUrl"])

# Save to file
with open("invoice.pdf", "wb") as f:
    f.write(content)
```

## Templates

### List Templates

```python
# List all templates
result = client.templates.list()
templates = result["data"]
meta = result["meta"]

print(f"Total templates: {meta['total']}")

for template in templates:
    print(f"{template['id']}: {template['name']} ({template['type']})")

# Paginated list
result = client.templates.list(page=2, limit=10)

# Search by name
result = client.templates.list(search="invoice")

# List PDF templates only
result = client.templates.list_pdf()

# List Excel templates only
result = client.templates.list_excel()
```

### Get Template Details

```python
# Get template by ID (supports UUID, shortId, or slug)
template = client.templates.get("tmpl_invoice")

print(f"Template: {template['name']}")
print(f"Type: {template['type']}")  # 'pdf' | 'excel'
print(f"Description: {template.get('description')}")
print(f"Created: {template['createdAt']}")
print(f"Updated: {template['updatedAt']}")

# View template variables
if "variables" in template and template["variables"]:
    print("\nVariables:")
    for variable in template["variables"]:
        print(f"  {variable['name']} ({variable['type']})")
        print(f"    Required: {variable.get('required', False)}")
        if "defaultValue" in variable:
            print(f"    Default: {variable['defaultValue']}")
```

## Webhooks

The SDK provides full CRUD access to webhook subscriptions and utilities for signature verification.

### List Webhooks

```python
result = client.webhooks.list()
webhooks = result.get("data", [])

for webhook in webhooks:
    print(f"{webhook['id']}: {webhook['url']}")
    print(f"  Events: {', '.join(webhook['events'])}")
    print(f"  Active: {webhook['isActive']}")
    print(f"  Created: {webhook['createdAt']}")
```

### Get Webhook Details

```python
webhook = client.webhooks.get("wh_abc123")

print(f"URL: {webhook['url']}")
print(f"Events: {webhook['events']}")
print(f"Active: {webhook['isActive']}")
print(f"Description: {webhook.get('description')}")
```

### Create Webhook

```python
webhook = client.webhooks.create(
    url="https://your-app.com/webhooks/rynko",
    events=["document.generated", "document.failed"],
    description="Production notifications",
)
print(f"Webhook ID: {webhook['id']}")
print(f"Secret: {webhook['secret']}")  # Store this securely
```

### Update Webhook

```python
webhook = client.webhooks.update(
    "wh_abc123",
    events=["document.generated"],
    is_active=False,
)
```

### Delete Webhook

```python
client.webhooks.delete("wh_abc123")
```

### Rotate Secret

```python
result = client.webhooks.rotate_secret("wh_abc123")
print(f"New secret: {result['secret']}")
```

### Test Webhook

```python
result = client.webhooks.test("wh_abc123")
print(f"Delivery status: {result['status']}")
```

### Webhook Deliveries

```python
# List deliveries for a webhook
result = client.webhooks.list_deliveries("wh_abc123")
for delivery in result.get("data", []):
    print(f"{delivery['id']}: {delivery['status']}")

# Retry a failed delivery
client.webhooks.retry_delivery("wh_abc123", "del_xyz789")
```

### Verify Webhook Signatures

When receiving webhooks, always verify the signature to ensure the request came from Rynko:

```python
import os
from rynko import verify_webhook_signature, WebhookSignatureError

# Flask example
@app.route('/webhooks/rynko', methods=['POST'])
def handle_webhook():
    signature = request.headers.get('X-Rynko-Signature')

    try:
        # The signature header contains both timestamp and signature: t=<ts>,v1=<hex>
        # Timestamp is validated automatically (default tolerance: 5 minutes)
        event = verify_webhook_signature(
            payload=request.data.decode('utf-8'),
            signature=signature,
            secret=os.environ['WEBHOOK_SECRET'],
            tolerance=300,  # Optional: tolerance in seconds (default: 300)
        )

        # Process the verified event
        print(f"Event type: {event['type']}")
        print(f"Event ID: {event['id']}")
        print(f"Timestamp: {event['timestamp']}")

        if event['type'] == 'document.generated':
            job_id = event['data']['jobId']
            download_url = event['data']['downloadUrl']
            metadata = event['data'].get('metadata', {})
            print(f"Document {job_id} ready: {download_url}")
            # Access metadata you passed during generation
            if metadata:
                print(f"Order ID: {metadata.get('orderId')}")
            # Download or process the document

        elif event['type'] == 'document.failed':
            job_id = event['data']['jobId']
            error = event['data']['errorMessage']
            metadata = event['data'].get('metadata', {})
            print(f"Document {job_id} failed: {error}")
            # Access metadata for correlation
            if metadata:
                print(f"Failed order: {metadata.get('orderId')}")
            # Handle failure (retry, notify user, etc.)

        elif event['type'] == 'batch.completed':
            batch_id = event['data']['batchId']
            total = event['data']['totalJobs']
            completed = event['data']['completedJobs']
            failed = event['data']['failedJobs']
            print(f"Batch {batch_id} done: {completed}/{total} succeeded, {failed} failed")

        elif event['type'] == 'document.downloaded':
            job_id = event['data']['jobId']
            downloaded_at = event['data']['downloadedAt']
            print(f"Document {job_id} downloaded at {downloaded_at}")

        return 'OK', 200

    except WebhookSignatureError as e:
        print(f"Invalid webhook signature: {e}")
        return 'Invalid signature', 401
```

#### Django Example

```python
import os
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rynko import verify_webhook_signature, WebhookSignatureError

@csrf_exempt
def webhook_handler(request):
    signature = request.headers.get('X-Rynko-Signature')

    try:
        event = verify_webhook_signature(
            payload=request.body.decode('utf-8'),
            signature=signature,
            secret=os.environ['WEBHOOK_SECRET'],
        )

        # Process the event
        if event['type'] == 'document.generated':
            # Handle document completion
            pass

        return HttpResponse('OK', status=200)

    except WebhookSignatureError:
        return HttpResponse('Invalid signature', status=401)
```

#### FastAPI Example

```python
import os
from fastapi import FastAPI, Request, HTTPException
from rynko import verify_webhook_signature, WebhookSignatureError

app = FastAPI()

@app.post("/webhooks/rynko")
async def webhook_handler(request: Request):
    signature = request.headers.get('X-Rynko-Signature')
    body = await request.body()

    try:
        event = verify_webhook_signature(
            payload=body.decode('utf-8'),
            signature=signature,
            secret=os.environ['WEBHOOK_SECRET'],
        )

        # Process the event
        if event['type'] == 'document.generated':
            # Handle document completion
            pass

        return {"status": "ok"}

    except WebhookSignatureError:
        raise HTTPException(status_code=401, detail="Invalid signature")
```

#### Webhook Event Types

| Event | Description | Payload |
|-------|-------------|---------|
| `document.generated` | Document successfully generated | `jobId`, `templateId`, `format`, `downloadUrl`, `fileSize`, `metadata` |
| `document.failed` | Document generation failed | `jobId`, `templateId`, `errorMessage`, `errorCode`, `metadata` |
| `document.downloaded` | Document was downloaded | `jobId`, `downloadedAt` |
| `batch.completed` | Batch generation finished | `batchId`, `templateId`, `format`, `totalJobs`, `completedJobs`, `failedJobs`, `metadata` |
| `flow.run.completed` | Flow run completed successfully | `runId`, `gateId`, `status`, `output` |
| `flow.run.approved` | Flow run approved by reviewer | `runId`, `gateId`, `status`, `approvalId` |
| `flow.run.rejected` | Flow run rejected by reviewer | `runId`, `gateId`, `status`, `reason` |
| `flow.run.review_required` | Flow run requires human review | `runId`, `gateId`, `status` |
| `flow.delivery.failed` | Flow delivery failed | `deliveryId`, `runId`, `error`, `attempts` |

#### Webhook Headers

Rynko sends these headers with each webhook request:

| Header | Description |
|--------|-------------|
| `X-Rynko-Signature` | HMAC-SHA256 signature (format: `t=<timestamp>,v1=<hex>`) |
| `X-Rynko-Timestamp` | Unix timestamp when the webhook was sent |
| `X-Rynko-Event-Id` | Unique event identifier |
| `X-Rynko-Event-Type` | Event type (e.g., `document.generated`) |

## Rynko Flow

[Rynko Flow](https://rynko.dev/flow) is an AI output validation gateway. Define gates with schemas and business rules, submit data for validation, handle human-in-the-loop approvals, and track webhook deliveries.

### Submit and Wait for Run

```python
# Submit data to a gate for validation
run = client.flow.submit_run(
    "gate_abc123",
    input={
        "customerName": "John Doe",
        "email": "john@example.com",
        "amount": 150.00,
    },
    metadata={"source": "checkout"},
    webhook_url="https://your-app.com/webhooks/flow",
)

print(f"Run ID: {run['id']}")
print(f"Status: {run['status']}")    # 'validated' or 'validation_failed'
print(f"Success: {run['success']}")  # True or False

# Check immediate validation result
if not run["success"]:
    print("Validation failed:", run.get("error"))

# For gates with rendering/approval steps, wait for terminal state
result = client.flow.wait_for_run(
    run["id"],
    poll_interval=2.0,   # Check every 2 seconds (default: 1.0)
    timeout=120.0,        # Wait up to 2 minutes (default: 60.0)
)

if result["status"] in ("validated", "approved"):
    print("Validation passed!", result.get("output"))
elif result["status"] == "validation_failed":
    print("Validation failed:", result.get("errors"))
elif result["status"] == "rejected":
    print("Rejected by reviewer:", result.get("errors"))
```

### List Gates

```python
# List all gates
result = client.flow.list_gates()
for gate in result["data"]:
    print(f"{gate['id']}: {gate['name']} ({gate['status']})")

# Get a specific gate
gate = client.flow.get_gate("gate_abc123")
print(f"Gate: {gate['name']}")
print(f"Schema: {gate.get('schema')}")
```

### List and Filter Runs

```python
# List all runs
result = client.flow.list_runs()

# Filter by status
result = client.flow.list_runs(status="approved")

# List runs for a specific gate
result = client.flow.list_runs_by_gate("gate_abc123")

# List active (in-progress) runs
result = client.flow.list_active_runs()
print(f"{len(result['data'])} runs in progress")

# Get a specific run
run = client.flow.get_run("run_abc123")
print(f"Status: {run['status']}")
```

### Gate Management

```python
# Create a gate
gate = client.flow.create_gate(
    name="Order Validation",
    description="Validates order data from AI agents",
    schema={
        "type": "object",
        "properties": {
            "orderId": {"type": "string"},
            "amount": {"type": "number", "minimum": 0},
        },
        "required": ["orderId", "amount"],
    },
)
print(f"Gate ID: {gate['id']}")

# Update a gate
client.flow.update_gate(gate["id"], name="Updated Order Validation")

# Update gate schema
client.flow.update_gate_schema(
    gate["id"],
    schema={"type": "object", "properties": {"orderId": {"type": "string"}}},
)

# Publish a gate
client.flow.publish_gate(gate["id"])

# Export and import gates
config = client.flow.export_gate(gate["id"])
imported = client.flow.import_gate(data=config)

# Rollback to previous version
client.flow.rollback_gate(gate["id"])

# Delete a gate
client.flow.delete_gate(gate["id"])
```

### Test and Validate

```python
# Dry-run test (no run created)
result = client.flow.test_gate(
    "gate_abc123",
    payload={"orderId": "ORD-001", "amount": 150.00},
)
print(f"Valid: {result.get('valid')}")

# Validate with run creation
result = client.flow.validate_gate(
    "gate_abc123",
    payload={"orderId": "ORD-001", "amount": 150.00},
    metadata={"source": "api_test"},
)
print(f"Validation ID: {result['validationId']}")

# Verify a previous validation
verified = client.flow.verify_validation(
    validation_id=result["validationId"],
    payload={"orderId": "ORD-001", "amount": 150.00},
)
```

### Manage Approvals

When a gate has approval rules, runs may enter a `pending_approval` state:

```python
# List pending approvals
result = client.flow.list_approvals(status="pending")

for approval in result["data"]:
    print(f"Approval {approval['id']} for run {approval['runId']}")

    # Approve with a note
    client.flow.approve(approval["id"], note="Looks good, approved.")

    # Or reject with a reason
    # client.flow.reject(approval["id"], reason="Amount exceeds limit.")
```

### Monitor Deliveries

Track webhook deliveries for completed runs:

```python
# List deliveries for a run
result = client.flow.list_deliveries("run_abc123")

for delivery in result["data"]:
    print(f"{delivery['id']}: {delivery['status']} → {delivery.get('url')}")

# Retry a failed delivery
retried = client.flow.retry_delivery("delivery_abc123")
print(f"Retry status: {retried['status']}")
```

### Run Payloads and Chains

```python
# Get the payload for a run
payload = client.flow.get_run_payload("run_abc123")
print(payload)

# Get a specific field from the payload
field_value = client.flow.get_run_payload("run_abc123", field="orderId")

# Get a chain of related runs by correlation ID
chain = client.flow.get_run_chain("corr_abc123")
for run in chain.get("runs", []):
    print(f"{run['id']}: {run['status']}")

# Get a transaction
txn = client.flow.get_transaction("txn_abc123")
print(f"Transaction status: {txn['status']}")
```

## Rynko Extract

[Rynko Extract](https://rynko.dev/extract) provides AI-powered document data extraction. Upload files, define schemas, and extract structured data from PDFs, images, and other documents.

### Create Extraction Job

```python
# Extract data from a document
with open("invoice.pdf", "rb") as f:
    job = client.extract.create_job(
        files=[("invoice.pdf", f.read(), "application/pdf")],
        instructions="Extract invoice number, date, and line items",
    )

print(f"Job ID: {job['id']}")
print(f"Status: {job['status']}")

# Check results
result = client.extract.get_job(job["id"])
if result["status"] == "completed":
    print(result["result"])

# List jobs
jobs = client.extract.list_jobs(status="completed", limit=10)

# Cancel a job
client.extract.cancel_job(job["id"])

# Check usage
usage = client.extract.get_usage()
print(f"Used: {usage['used']}, Remaining: {usage['remaining']}")
```

### Schema Discovery

```python
# Discover schema from sample documents
with open("invoice.pdf", "rb") as f:
    schema = client.extract.discover(
        files=[("invoice.pdf", f.read(), "application/pdf")],
        instructions="Find all invoice fields",
    )
print(f"Discovered schema: {schema}")
```

### Extraction Configs

```python
# Create a reusable extraction config
config = client.extract.create_config(
    name="Invoice Extractor",
    schema={
        "type": "object",
        "properties": {
            "invoiceNumber": {"type": "string"},
            "date": {"type": "string"},
            "total": {"type": "number"},
        },
    },
    instructions="Extract all invoice fields",
)

# Publish the config
client.extract.publish_config(config["id"])

# Run extraction using a config
with open("invoice.pdf", "rb") as f:
    job = client.extract.run_config(
        config["id"],
        files=[("invoice.pdf", f.read(), "application/pdf")],
    )

# List configs
configs = client.extract.list_configs(status="published")

# Update a config
client.extract.update_config(config["id"], name="Updated Extractor")

# Version management
versions = client.extract.get_config_versions(config["id"])
client.extract.restore_config_version(config["id"], "ver_xyz")

# Delete a config
client.extract.delete_config(config["id"])
```

### Flow Integration

```python
# Extract with Flow gate validation
with open("invoice.pdf", "rb") as f:
    job = client.extract.extract_with_gate(
        "gate_abc123",
        files=[("invoice.pdf", f.read(), "application/pdf")],
        instructions="Extract invoice data",
    )

# Submit files to a Flow gate pipeline
with open("document.pdf", "rb") as f:
    run = client.extract.submit_file_run(
        "gate_abc123",
        files=[("document.pdf", f.read(), "application/pdf")],
        metadata={"source": "upload"},
    )
print(f"Run ID: {run['id']}")
```

## Async Client

For async applications (FastAPI, aiohttp, etc.), use `AsyncRynko`:

```python
from rynko import AsyncRynko
import asyncio

async def main():
    async with AsyncRynko(api_key="your_api_key") as client:
        # Get user info
        user = await client.me()
        print(f"Authenticated as: {user['email']}")

        # Queue document generation
        job = await client.documents.generate_pdf(
            template_id="tmpl_invoice",
            variables={"invoiceNumber": "INV-001"},
        )
        print(f"Job queued: {job['jobId']}")

        # Wait for completion
        completed = await client.documents.wait_for_completion(job["jobId"])
        print(f"Download URL: {completed['downloadUrl']}")

        # List templates
        result = await client.templates.list()
        for template in result["data"]:
            print(f"Template: {template['name']}")

        # Submit a Flow run
        run = await client.flow.submit_run(
            "gate_abc123",
            input={"name": "John Doe", "amount": 150.00},
        )
        result = await client.flow.wait_for_run(run["id"])
        print(f"Flow result: {result['status']}")

asyncio.run(main())
```

### Async with FastAPI

```python
from fastapi import FastAPI, Depends
from rynko import AsyncRynko
import os

app = FastAPI()

async def get_rynko():
    async with AsyncRynko(api_key=os.environ["RYNKO_API_KEY"]) as client:
        yield client

@app.post("/generate-invoice")
async def generate_invoice(
    invoice_data: dict,
    client: AsyncRynko = Depends(get_rynko)
):
    job = await client.documents.generate_pdf(
        template_id="tmpl_invoice",
        variables=invoice_data,
    )

    completed = await client.documents.wait_for_completion(job["jobId"])
    return {"download_url": completed["downloadUrl"]}
```

## Configuration

```python
client = Rynko(
    # Required: Your API key
    api_key="your_api_key",

    # Optional: Custom base URL (default: https://api.rynko.dev)
    base_url="https://api.rynko.dev",

    # Optional: Request timeout in seconds (default: 30)
    timeout=30.0,

    # Optional: Custom headers for all requests
    headers={"X-Custom-Header": "value"},
)
```

### Retry Configuration

Automatic retry with exponential backoff is enabled by default:

```python
from rynko import Rynko, RetryConfig

# Custom retry configuration
client = Rynko(
    api_key="your_api_key",
    retry=RetryConfig(
        max_attempts=3,           # Maximum retry attempts (default: 5)
        initial_delay=0.5,        # Initial delay in seconds (default: 1.0)
        max_delay=10.0,           # Maximum delay in seconds (default: 30.0)
        max_jitter=0.5,           # Maximum jitter in seconds (default: 1.0)
        retryable_statuses={429, 503, 504},  # HTTP statuses to retry (default)
    ),
)

# Disable retry entirely
client = Rynko(api_key="your_api_key", retry=False)
```

### Environment Variables

We recommend using environment variables for configuration:

```bash
# .env
RYNKO_API_KEY=your_api_key_here
WEBHOOK_SECRET=your_webhook_secret_here
```

```python
import os
from dotenv import load_dotenv
from rynko import Rynko

load_dotenv()

client = Rynko(api_key=os.environ["RYNKO_API_KEY"])
```

## Error Handling

```python
from rynko import Rynko, RynkoError

client = Rynko(api_key="your_api_key")

try:
    job = client.documents.generate_pdf(
        template_id="invalid_template",
        variables={},
    )
except RynkoError as e:
    print(f"API Error: {e.message}")
    print(f"Error Code: {e.code}")
    print(f"Status Code: {e.status_code}")

    # Handle specific error codes
    if e.code == "ERR_TMPL_001":
        print("Template not found")
    elif e.code == "ERR_TMPL_003":
        print("Template validation failed")
    elif e.code == "ERR_QUOTA_001":
        print("Document quota exceeded - upgrade your plan")
    elif e.code == "ERR_AUTH_001":
        print("Invalid API key")
    elif e.code == "ERR_AUTH_004":
        print("API key expired or revoked")
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `ERR_AUTH_001` | Invalid credentials / API key |
| `ERR_AUTH_004` | Token expired or revoked |
| `ERR_TMPL_001` | Template not found |
| `ERR_TMPL_003` | Template validation failed |
| `ERR_DOC_001` | Document job not found |
| `ERR_DOC_004` | Document generation failed |
| `ERR_QUOTA_001` | Document quota exceeded |
| `ERR_QUOTA_002` | Rate limit exceeded |

## Context Manager

Use the client as a context manager to ensure proper resource cleanup:

```python
# Synchronous
with Rynko(api_key="your_api_key") as client:
    job = client.documents.generate_pdf(
        template_id="tmpl_invoice",
        variables={"invoiceNumber": "INV-001"},
    )
    completed = client.documents.wait_for_completion(job["jobId"])
    print(f"Download URL: {completed['downloadUrl']}")

# Asynchronous
async with AsyncRynko(api_key="your_api_key") as client:
    job = await client.documents.generate_pdf(
        template_id="tmpl_invoice",
        variables={"invoiceNumber": "INV-001"},
    )
    completed = await client.documents.wait_for_completion(job["jobId"])
    print(f"Download URL: {completed['downloadUrl']}")
```

## API Reference

### Client Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `me()` | `Dict[str, Any]` | Get current authenticated user |
| `verify_api_key()` | `bool` | Verify API key is valid |

### Documents Resource

| Method | Returns | Description |
|--------|---------|-------------|
| `generate(...)` | `Dict[str, Any]` | Generate a document (PDF, Excel, or CSV) |
| `generate_pdf(...)` | `Dict[str, Any]` | Generate a PDF document |
| `generate_excel(...)` | `Dict[str, Any]` | Generate an Excel document |
| `generate_batch(...)` | `Dict[str, Any]` | Generate multiple documents |
| `get_job(job_id)` | `Dict[str, Any]` | Get document job by ID |
| `list_jobs(...)` | `Dict[str, Any]` | List/search document jobs |
| `delete(job_id)` | `Dict[str, Any]` | Delete a document job |
| `get_batch(batch_id)` | `Dict[str, Any]` | Get batch by ID |
| `wait_for_completion(job_id, ...)` | `Dict[str, Any]` | Poll until job completes or fails |
| `wait_for_batch_completion(batch_id, ...)` | `Dict[str, Any]` | Poll until batch reaches terminal state |
| `download(download_url)` | `bytes` | Download generated document from signed URL |
| `retry(job_id)` | `Dict[str, Any]` | Retry a failed document job |
| `cancel(job_id)` | `Dict[str, Any]` | Cancel a queued or processing job |

### Templates Resource

| Method | Returns | Description |
|--------|---------|-------------|
| `get(template_id)` | `Dict[str, Any]` | Get template by ID (UUID, shortId, or slug) |
| `list(...)` | `Dict[str, Any]` | List all templates |
| `list_pdf(...)` | `Dict[str, Any]` | List PDF templates only |
| `list_excel(...)` | `Dict[str, Any]` | List Excel templates only |

### Webhooks Resource

| Method | Returns | Description |
|--------|---------|-------------|
| `get(webhook_id)` | `Dict[str, Any]` | Get webhook subscription by ID |
| `list()` | `Dict[str, Any]` | List all webhook subscriptions |
| `create(...)` | `Dict[str, Any]` | Create a webhook subscription |
| `update(webhook_id, ...)` | `Dict[str, Any]` | Update a webhook subscription |
| `delete(webhook_id)` | `Dict[str, Any]` | Delete a webhook subscription |
| `rotate_secret(webhook_id)` | `Dict[str, Any]` | Rotate webhook signing secret |
| `test(webhook_id)` | `Dict[str, Any]` | Send a test event |
| `list_deliveries(webhook_id, ...)` | `Dict[str, Any]` | List deliveries for a webhook |
| `retry_delivery(webhook_id, delivery_id)` | `Dict[str, Any]` | Retry a failed delivery |

### Flow Resource

| Method | Returns | Description |
|--------|---------|-------------|
| `list_gates(...)` | `Dict[str, Any]` | List all gates |
| `get_gate(gate_id)` | `Dict[str, Any]` | Get gate by ID |
| `submit_run(gate_id, ...)` | `Dict[str, Any]` | Submit a run for validation |
| `get_run(run_id)` | `Dict[str, Any]` | Get run by ID |
| `list_runs(...)` | `Dict[str, Any]` | List all runs |
| `list_runs_by_gate(gate_id, ...)` | `Dict[str, Any]` | List runs for a gate |
| `list_active_runs(...)` | `Dict[str, Any]` | List active runs |
| `wait_for_run(run_id, ...)` | `Dict[str, Any]` | Poll until run reaches terminal state |
| `create_gate(...)` | `Dict[str, Any]` | Create a gate |
| `update_gate(gate_id, ...)` | `Dict[str, Any]` | Update a gate |
| `delete_gate(gate_id)` | `Dict[str, Any]` | Delete a gate |
| `update_gate_schema(gate_id, ...)` | `Dict[str, Any]` | Update gate schema |
| `publish_gate(gate_id)` | `Dict[str, Any]` | Publish a gate |
| `rollback_gate(gate_id, ...)` | `Dict[str, Any]` | Rollback gate to previous version |
| `export_gate(gate_id)` | `Dict[str, Any]` | Export gate configuration |
| `import_gate(...)` | `Dict[str, Any]` | Import gate from configuration |
| `test_gate(gate_id, ...)` | `Dict[str, Any]` | Dry-run test (no run created) |
| `validate_gate(gate_id, ...)` | `Dict[str, Any]` | Validate payload (creates run) |
| `verify_validation(...)` | `Dict[str, Any]` | Verify a validation result |
| `list_approvals(...)` | `Dict[str, Any]` | List approvals |
| `approve(approval_id, ...)` | `Dict[str, Any]` | Approve a pending approval |
| `reject(approval_id, ...)` | `Dict[str, Any]` | Reject a pending approval |
| `list_deliveries(run_id, ...)` | `Dict[str, Any]` | List deliveries for a run |
| `retry_delivery(delivery_id)` | `Dict[str, Any]` | Retry a failed delivery |
| `get_run_payload(run_id, ...)` | `Dict[str, Any]` | Get run payload |
| `get_run_chain(correlation_id)` | `Dict[str, Any]` | Get chain of related runs |
| `get_transaction(transaction_id)` | `Dict[str, Any]` | Get transaction by ID |

### Extract Resource

| Method | Returns | Description |
|--------|---------|-------------|
| `create_job(...)` | `Dict[str, Any]` | Create an extraction job |
| `get_job(job_id)` | `Dict[str, Any]` | Get extraction job by ID |
| `list_jobs(...)` | `Dict[str, Any]` | List extraction jobs |
| `cancel_job(job_id)` | `Dict[str, Any]` | Cancel an extraction job |
| `get_usage()` | `Dict[str, Any]` | Get extraction usage statistics |
| `discover(...)` | `Dict[str, Any]` | Discover schema from files |
| `create_config(...)` | `Dict[str, Any]` | Create an extraction config |
| `get_config(config_id)` | `Dict[str, Any]` | Get extraction config by ID |
| `list_configs(...)` | `Dict[str, Any]` | List extraction configs |
| `update_config(config_id, ...)` | `Dict[str, Any]` | Update an extraction config |
| `delete_config(config_id)` | `Dict[str, Any]` | Delete an extraction config |
| `publish_config(config_id)` | `Dict[str, Any]` | Publish an extraction config |
| `get_config_versions(config_id)` | `Dict[str, Any]` | Get config version history |
| `restore_config_version(config_id, version_id)` | `Dict[str, Any]` | Restore config to a version |
| `run_config(config_id, ...)` | `Dict[str, Any]` | Run extraction config on files |
| `extract_with_gate(gate_id, ...)` | `Dict[str, Any]` | Extract with Flow gate validation |
| `submit_file_run(gate_id, ...)` | `Dict[str, Any]` | Submit files to Flow gate pipeline |

### Utilities

| Function | Returns | Description |
|----------|---------|-------------|
| `verify_webhook_signature(...)` | `Dict[str, Any]` | Verify signature and parse webhook event |

## Examples

See the [`examples/`](./examples) directory for runnable code samples:

- [basic_generate.py](./examples/basic_generate.py) - Generate a PDF and wait for completion
- [batch_generate.py](./examples/batch_generate.py) - Generate multiple documents
- [webhook_handler.py](./examples/webhook_handler.py) - Flask webhook endpoint
- [error_handling.py](./examples/error_handling.py) - Handle API errors
- [flow_submit_and_wait.py](./examples/flow_submit_and_wait.py) - Submit a run and wait for validation
- [flow_approval_workflow.py](./examples/flow_approval_workflow.py) - Programmatic approval automation
- [flow_webhook_handler.py](./examples/flow_webhook_handler.py) - Flask webhook handler for Flow events

For complete project templates with full setup, see the [developer-resources](https://github.com/rynko-dev/developer-resources) repository.

## Requirements

- Python 3.8+
- httpx 0.24+

## License

MIT

## Support

- **Documentation**: https://docs.rynko.dev/sdk/python
- **API Reference**: https://docs.rynko.dev/api
- **Examples**: https://github.com/rynko-dev/developer-resources
- **GitHub Issues**: https://github.com/rynko-dev/sdk-python/issues
- **Email**: support@rynko.dev
