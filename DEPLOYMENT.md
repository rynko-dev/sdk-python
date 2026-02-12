# Python SDK Deployment Guide

This guide covers publishing and maintaining the Rynko Python SDK (`rynko`).

## Prerequisites

- Python 3.8 or higher
- PyPI account with publish access
- GitHub repository access
- `build` and `twine` packages installed

## Package Overview

```
rynko/
├── rynko/
│   ├── __init__.py      # Package exports
│   ├── client.py        # Rynko and AsyncRynko clients
│   ├── exceptions.py    # Error classes
│   ├── types.py         # TypedDict definitions
│   ├── http.py          # HTTP client (sync/async)
│   ├── webhooks.py      # Webhook signature verification
│   └── resources/       # API resource classes
├── pyproject.toml
└── README.md
```

## Build Process

### 1. Set Up Development Environment

```bash
cd integrations/sdk-python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install development dependencies
pip install -e ".[dev]"
```

### 2. Run Tests

```bash
pytest
```

### 3. Run Linting

```bash
# Type checking
mypy rynko

# Code style
ruff check rynko
ruff format rynko
```

### 4. Build Package

```bash
python -m build
```

This creates:
- `dist/rynko-X.Y.Z.tar.gz` (source distribution)
- `dist/rynko-X.Y.Z-py3-none-any.whl` (wheel)

## Publishing to PyPI

### Initial Setup

1. **Create PyPI Account**:
   - Register at https://pypi.org/account/register/
   - Enable 2FA

2. **Create API Token**:
   - Go to Account Settings → API tokens
   - Create token with upload scope

3. **Configure twine**:
   Create `~/.pypirc`:
   ```ini
   [pypi]
   username = __token__
   password = pypi-your-token-here
   ```

### Publishing a New Version

1. **Update Version** in `pyproject.toml`:
   ```toml
   [project]
   version = "1.0.1"
   ```

2. **Update Changelog**

3. **Build**:
   ```bash
   rm -rf dist/
   python -m build
   ```

4. **Test Upload to TestPyPI** (optional):
   ```bash
   twine upload --repository testpypi dist/*
   ```

5. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```

6. **Tag Release**:
   ```bash
   git tag sdk-python-v1.0.1
   git push origin main --tags
   ```

### Automated Publishing (CI/CD)

Add to `.github/workflows/publish-python.yml`:

```yaml
name: Publish Python SDK

on:
  push:
    tags:
      - 'sdk-python-v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install build tools
        run: pip install build twine

      - name: Build package
        working-directory: integrations/sdk-python
        run: python -m build

      - name: Publish to PyPI
        working-directory: integrations/sdk-python
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
        run: twine upload dist/*
```

## Version Management

### Semantic Versioning

- **MAJOR**: Breaking API changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Changelog

Maintain `CHANGELOG.md`:

```markdown
# Changelog

## [1.1.0] - 2025-01-15
### Added
- New `documents.wait_for_completion()` method
- Support for workspace ID in document generation

### Fixed
- Timeout handling in async client

## [1.0.0] - 2025-01-01
### Initial Release
- Sync and async clients
- Document generation (PDF and Excel)
- Template listing and retrieval
- Webhook signature verification
```

## Configuration Requirements

### Environment Variables

Users should set:
```bash
export RYNKO_API_KEY=your_api_key
```

### SDK Configuration

```python
from rynko import Rynko

client = Rynko(
    api_key=os.environ["RYNKO_API_KEY"],
    # Optional
    base_url="https://api.rynko.dev",
    timeout=30.0,
)
```

## API Compatibility

### Backend Requirements

The SDK requires these Rynko API endpoints:

| Endpoint | SDK Method |
|----------|------------|
| `GET /api/auth/verify` | `client.me()` / `client.verify_api_key()` |
| `POST /api/v1/documents/generate` | `client.documents.generate()` / `generate_pdf()` / `generate_excel()` |
| `POST /api/v1/documents/generate/batch` | `client.documents.generate_batch()` |
| `GET /api/v1/documents/jobs/:id` | `client.documents.get_job()` |
| `GET /api/v1/documents/jobs` | `client.documents.list_jobs()` |
| `GET /api/v1/templates` | `client.templates.list()` |
| `GET /api/v1/templates/:id` | `client.templates.get()` |
| `GET /api/v1/webhook-subscriptions` | `client.webhooks.list()` |
| `GET /api/v1/webhook-subscriptions/:id` | `client.webhooks.get()` |

### Python Version Compatibility

| SDK Version | Python Versions |
|-------------|-----------------|
| 1.x | 3.8, 3.9, 3.10, 3.11, 3.12 |

## Testing

### Unit Tests

```bash
pytest tests/
```

### Integration Tests

Create `.env.test`:
```bash
RYNKO_API_KEY=test_api_key
RYNKO_BASE_URL=http://localhost:3000
```

Run integration tests:
```bash
pytest tests/integration/
```

### Test Coverage

```bash
pytest --cov=rynko --cov-report=html
```

### Manual Testing

```python
from rynko import Rynko

client = Rynko(
    api_key="your_test_key",
    base_url="http://localhost:3000",
)

# Test authentication
user = client.me()
print(f"Authenticated as: {user['email']}")

# Test document generation
job = client.documents.generate_pdf(
    template_id="tmpl_test",
    variables={"name": "Test"},
)
print(f"Job queued: {job['jobId']}")

# Wait for completion
completed = client.documents.wait_for_completion(job["jobId"])
print(f"Download URL: {completed['downloadUrl']}")
```

### Async Testing

```python
import asyncio
from rynko import AsyncRynko

async def test_async():
    async with AsyncRynko(api_key="your_key") as client:
        user = await client.me()
        print(f"Authenticated as: {user['email']}")

asyncio.run(test_async())
```

## Documentation

### API Documentation

Generate Sphinx documentation:

```bash
cd docs
make html
```

### README Updates

Update `README.md` with:
- Installation instructions
- Quick start examples
- API reference
- Error handling
- Async usage examples

## Type Hints

The SDK uses TypedDict for all response types:

```python
from rynko.types import GenerateResponse

result: GenerateResponse = client.documents.generate_pdf(...)
```

Verify types with mypy:
```bash
mypy rynko --strict
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure `httpx` is installed: `pip install httpx`
   - Check Python version >= 3.8

2. **Async Runtime Errors**
   - Use `async with` for proper cleanup
   - Don't mix sync and async clients

3. **SSL Errors**
   - Update certificates: `pip install certifi`
   - Check network/proxy settings

4. **Publish Failures**
   - Verify PyPI token is valid
   - Check version doesn't already exist
   - Ensure all metadata is valid

### Support Channels

- GitHub Issues: Report bugs and feature requests
- Email: sdk-support@rynko.dev
- Documentation: https://docs.rynko.dev/sdk/python

## Security

### API Key Handling

- Never commit API keys to source control
- Use environment variables
- Rotate keys if compromised

### Dependency Updates

Regularly update dependencies:
```bash
pip install --upgrade httpx
pip audit  # if pip-audit is installed
```

### Vulnerability Disclosure

Report security issues to: security@rynko.dev

## Framework Examples

### Flask

```python
from flask import Flask, request
from rynko import Rynko, verify_webhook_signature

app = Flask(__name__)
client = Rynko(api_key=os.environ["RYNKO_API_KEY"])

@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Rynko-Signature")
    event = verify_webhook_signature(
        payload=request.data.decode("utf-8"),
        signature=signature,
        secret=os.environ["WEBHOOK_SECRET"],
    )
    # Process event...
    return "OK"
```

### FastAPI

```python
from fastapi import FastAPI, Request, HTTPException
from rynko import AsyncRynko, verify_webhook_signature

app = FastAPI()

@app.on_event("startup")
async def startup():
    app.state.rynko = AsyncRynko(api_key=os.environ["RYNKO_API_KEY"])

@app.on_event("shutdown")
async def shutdown():
    await app.state.rynko.close()

@app.post("/generate")
async def generate_document(template_id: str, format: str = "pdf"):
    result = await app.state.rynko.documents.generate(
        template_id=template_id,
        format=format,
    )
    return result
```

### Django

```python
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rynko import Rynko

client = Rynko(api_key=settings.RYNKO_API_KEY)

def generate_document(request):
    result = client.documents.generate_pdf(
        template_id=request.POST["template_id"],
        variables=request.POST.get("variables", {}),
    )
    return JsonResponse(result)
```
