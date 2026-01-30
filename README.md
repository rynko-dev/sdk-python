# rynko

Official Python SDK for [Rynko](https://rynko.dev) - the document generation platform with unified template design for PDF and Excel documents.

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
- [Templates](#templates)
  - [List Templates](#list-templates)
  - [Get Template Details](#get-template-details)
- [Webhooks](#webhooks)
  - [List Webhooks](#list-webhooks)
  - [Verify Webhook Signatures](#verify-webhook-signatures)
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

Or with optional async support:

```bash
pip install rynko[async]
```

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
- **Workspace support** - Generate documents in specific workspaces
- **Webhook verification** - Secure HMAC signature verification for incoming webhooks
- **Polling utility** - Built-in `wait_for_completion()` method with configurable timeout
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
print(f"Team: {user.get('teamName')}")
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
    workspace_id="ws_abc123",       # Generate in specific workspace
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
# Each dict in the documents list contains variables for one document
batch = client.documents.generate_batch(
    template_id="tmpl_invoice",
    format="pdf",
    documents=[
        {
            "invoiceNumber": "INV-001",
            "customerName": "John Doe",
            "total": 150.00,
        },
        {
            "invoiceNumber": "INV-002",
            "customerName": "Jane Smith",
            "total": 275.50,
        },
        {
            "invoiceNumber": "INV-003",
            "customerName": "Bob Wilson",
            "total": 89.99,
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

# Filter by format
result = client.documents.list_jobs(format="pdf")

# Filter by template
result = client.documents.list_jobs(template_id="tmpl_invoice")

# Filter by workspace
result = client.documents.list_jobs(workspace_id="ws_abc123")

# Filter by date range
result = client.documents.list_jobs(
    date_from="2026-01-01",
    date_to="2026-01-31",
)

# Combine filters
result = client.documents.list_jobs(
    status="completed",
    format="pdf",
    template_id="tmpl_invoice",
    limit=50,
)
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

Webhook subscriptions are managed through the [Rynko Dashboard](https://app.rynko.dev). The SDK provides read-only access to view webhooks and utilities for signature verification.

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

### Verify Webhook Signatures

When receiving webhooks, always verify the signature to ensure the request came from Rynko:

```python
import os
from rynko import verify_webhook_signature, WebhookSignatureError

# Flask example
@app.route('/webhooks/rynko', methods=['POST'])
def handle_webhook():
    signature = request.headers.get('X-Rynko-Signature')
    timestamp = request.headers.get('X-Rynko-Timestamp')

    try:
        event = verify_webhook_signature(
            payload=request.data.decode('utf-8'),
            signature=signature,
            timestamp=timestamp,  # Optional but recommended for replay protection
            secret=os.environ['WEBHOOK_SECRET'],
        )

        # Process the verified event
        print(f"Event type: {event['type']}")
        print(f"Event ID: {event['id']}")
        print(f"Timestamp: {event['timestamp']}")

        if event['type'] == 'document.generated':
            job_id = event['data']['jobId']
            download_url = event['data']['downloadUrl']
            print(f"Document {job_id} ready: {download_url}")
            # Download or process the document

        elif event['type'] == 'document.failed':
            job_id = event['data']['jobId']
            error = event['data']['error']
            print(f"Document {job_id} failed: {error}")
            # Handle failure (retry, notify user, etc.)

        elif event['type'] == 'document.downloaded':
            job_id = event['data']['jobId']
            print(f"Document {job_id} was downloaded")

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
    timestamp = request.headers.get('X-Rynko-Timestamp')

    try:
        event = verify_webhook_signature(
            payload=request.body.decode('utf-8'),
            signature=signature,
            timestamp=timestamp,
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
    timestamp = request.headers.get('X-Rynko-Timestamp')
    body = await request.body()

    try:
        event = verify_webhook_signature(
            payload=body.decode('utf-8'),
            signature=signature,
            timestamp=timestamp,
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
| `document.generated` | Document successfully generated | `jobId`, `templateId`, `format`, `downloadUrl`, `fileSize` |
| `document.failed` | Document generation failed | `jobId`, `templateId`, `error`, `errorCode` |
| `document.downloaded` | Document was downloaded | `jobId`, `downloadedAt` |

#### Webhook Headers

Rynko sends these headers with each webhook request:

| Header | Description |
|--------|-------------|
| `X-Rynko-Signature` | HMAC-SHA256 signature (format: `v1=<hex>`) |
| `X-Rynko-Timestamp` | Unix timestamp when the webhook was sent |
| `X-Rynko-Event-Id` | Unique event identifier |
| `X-Rynko-Event-Type` | Event type (e.g., `document.generated`) |

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
| `wait_for_completion(job_id, ...)` | `Dict[str, Any]` | Poll until job completes or fails |

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
