# renderbase

Official Python SDK for Renderbase - the document generation platform with unified template design for PDF and Excel documents.

## Installation

```bash
pip install renderbase
```

## Quick Start

```python
from renderbase import Renderbase

client = Renderbase(api_key="your_api_key")

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
- **Type hints** - Full type annotation support
- **PDF generation** - Generate PDF documents from templates
- **Excel generation** - Generate Excel documents from templates
- **Batch generation** - Generate multiple documents at once
- **Workspace support** - Generate documents in specific workspaces
- **Webhook verification** - Secure signature verification
- **Polling utility** - Wait for document completion

## Usage Examples

### Generate PDF Document

```python
# Queue document generation
job = client.documents.generate_pdf(
    template_id="tmpl_invoice",
    variables={
        "invoiceNumber": "INV-001",
        "customerName": "John Doe",
        "items": [
            {"description": "Product A", "quantity": 2, "price": 50.00},
            {"description": "Product B", "quantity": 1, "price": 50.00},
        ],
        "total": 150.00,
    },
)

# Wait for completion and get download URL
completed = client.documents.wait_for_completion(job["jobId"])
print(f"Download URL: {completed['downloadUrl']}")
```

### Generate Excel Document

```python
job = client.documents.generate_excel(
    template_id="tmpl_report",
    variables={
        "reportMonth": "January 2026",
        "salesData": [
            {"region": "North", "sales": 10000},
            {"region": "South", "sales": 15000},
            {"region": "East", "sales": 12000},
        ],
    },
)

completed = client.documents.wait_for_completion(job["jobId"])
print(f"Download URL: {completed['downloadUrl']}")
```

### Generate Batch Documents

```python
# Queue batch generation - each dict in documents list contains variables for one document
batch = client.documents.generate_batch(
    template_id="tmpl_invoice",
    format="pdf",
    documents=[
        {"invoiceNumber": "INV-001", "customerName": "John Doe"},
        {"invoiceNumber": "INV-002", "customerName": "Jane Smith"},
        {"invoiceNumber": "INV-003", "customerName": "Bob Wilson"},
    ],
)

print(f"Batch ID: {batch['batchId']}")
print(f"Total jobs: {batch['totalJobs']}")
print(f"Estimated wait: {batch['estimatedWaitSeconds']} seconds")
```

### Wait for Document Completion

```python
# Generate and wait for completion
job = client.documents.generate_pdf(
    template_id="tmpl_invoice",
    variables={"invoiceNumber": "INV-001"},
)

completed = client.documents.wait_for_completion(
    job["jobId"],
    poll_interval=1.0,  # Check every 1 second
    timeout=30.0,       # Wait up to 30 seconds
)

print(f"Download URL: {completed['downloadUrl']}")
```

### List Document Jobs

```python
# List recent jobs
result = client.documents.list_jobs(limit=20)

# Filter by status
result = client.documents.list_jobs(status="completed", format="pdf")

# Filter by workspace
result = client.documents.list_jobs(
    workspace_id="ws_abc123",
    date_from="2026-01-01",
)

# Get specific job
job = client.documents.get_job("job_abc123")
```

### Work with Templates

```python
# List all templates
templates = client.templates.list()

# List by type
pdf_templates = client.templates.list(type="pdf")
excel_templates = client.templates.list(type="excel")

# Get template details
template = client.templates.get("tmpl_abc123")
print(f"Variables: {template['variables']}")
```

### Manage Webhooks

```python
# Create a webhook subscription
webhook = client.webhooks.create(
    url="https://your-app.com/webhooks/renderbase",
    events=["document.completed", "document.failed", "batch.completed"],
    name="My Document Webhook",
)

# Save the secret for verification!
print(f"Webhook secret: {webhook['secret']}")

# List webhooks
webhooks = client.webhooks.list()

# Delete a webhook
client.webhooks.delete("wh_abc123")
```

### Verify Webhook Signatures

```python
from renderbase import verify_webhook_signature, WebhookSignatureError

# Flask example
@app.route('/webhooks/renderbase', methods=['POST'])
def handle_webhook():
    signature = request.headers.get('X-Renderbase-Signature')

    try:
        event = verify_webhook_signature(
            payload=request.data.decode('utf-8'),
            signature=signature,
            secret=os.environ['WEBHOOK_SECRET'],
        )

        # Process the verified event
        if event['type'] == 'document.completed':
            print(f"Document ready: {event['data']['downloadUrl']}")
        elif event['type'] == 'document.failed':
            print(f"Document failed: {event['data']['error']}")
        elif event['type'] == 'batch.completed':
            print(f"Batch completed: {event['data']['batchId']}")

        return 'OK', 200
    except WebhookSignatureError as e:
        return f'Invalid signature: {e}', 400
```

## Async Client

For async applications, use `AsyncRenderbase`:

```python
from renderbase import AsyncRenderbase
import asyncio

async def main():
    async with AsyncRenderbase(api_key="your_api_key") as client:
        # Queue document generation
        job = await client.documents.generate_pdf(
            template_id="tmpl_invoice",
            variables={"invoiceNumber": "INV-001"},
        )
        print(f"Job queued: {job['jobId']}")

        # Wait for completion
        completed = await client.documents.wait_for_completion(job["jobId"])
        print(f"Download URL: {completed['downloadUrl']}")

asyncio.run(main())
```

## Configuration

```python
client = Renderbase(
    # Required: Your API key
    api_key="your_api_key",

    # Optional: Custom base URL (default: https://api.renderbase.dev)
    base_url="https://api.renderbase.dev",

    # Optional: Request timeout in seconds (default: 30)
    timeout=30.0,

    # Optional: Custom headers
    headers={"X-Custom-Header": "value"},
)
```

## Error Handling

```python
from renderbase import Renderbase, RenderbaseError

client = Renderbase(api_key="your_api_key")

try:
    result = client.documents.generate_pdf(
        template_id="invalid_template",
    )
except RenderbaseError as e:
    print(f"API Error: {e.message}")
    print(f"Code: {e.code}")
    print(f"Status: {e.status_code}")
```

## Context Manager

Use the client as a context manager to ensure proper cleanup:

```python
with Renderbase(api_key="your_api_key") as client:
    job = client.documents.generate_pdf(
        template_id="tmpl_invoice",
        variables={"invoiceNumber": "INV-001"},
    )
    completed = client.documents.wait_for_completion(job["jobId"])
    print(f"Download URL: {completed['downloadUrl']}")
```

## API Reference

### Client Methods

- `client.me()` - Get current authenticated user
- `client.verify_api_key()` - Verify API key is valid

### Documents Resource

- `client.documents.generate(...)` - Generate a document (PDF or Excel)
- `client.documents.generate_pdf(...)` - Generate a PDF document
- `client.documents.generate_excel(...)` - Generate an Excel document
- `client.documents.generate_batch(...)` - Generate batch documents
- `client.documents.get_job(job_id)` - Get document job by ID
- `client.documents.list_jobs(...)` - List/search document jobs
- `client.documents.wait_for_completion(job_id, ...)` - Wait for job completion

### Templates Resource

- `client.templates.get(template_id)` - Get template by ID
- `client.templates.list(...)` - List templates

### Webhooks Resource

- `client.webhooks.create(...)` - Create webhook subscription
- `client.webhooks.get(webhook_id)` - Get webhook by ID
- `client.webhooks.list()` - List webhooks
- `client.webhooks.update(...)` - Update webhook
- `client.webhooks.delete(webhook_id)` - Delete webhook

### Utilities

- `verify_webhook_signature(...)` - Verify webhook signature

## Requirements

- Python 3.8+
- httpx 0.24+

## License

MIT

## Support

- Documentation: https://docs.renderbase.dev/sdk/python
- API Reference: https://docs.renderbase.dev/api
- Support: support@renderbase.dev
