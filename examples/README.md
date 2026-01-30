# Examples

This directory contains example code demonstrating how to use the Rynko Python SDK.

## Prerequisites

- Python 3.8+
- A Rynko API key ([get one here](https://app.rynko.dev/settings/api-keys))
- At least one template created in your workspace

## Running Examples

From the SDK root directory:

```bash
# Install the SDK
pip install -e .

# Run an example
RYNKO_API_KEY=your_key python examples/basic_generate.py
```

## Available Examples

| Example | Description |
|---------|-------------|
| [basic_generate.py](./basic_generate.py) | Generate a PDF and wait for completion |
| [batch_generate.py](./batch_generate.py) | Generate multiple documents in one request |
| [webhook_handler.py](./webhook_handler.py) | Flask server that verifies and handles webhooks |
| [error_handling.py](./error_handling.py) | Handle API errors gracefully |

## Webhook Handler Dependencies

The webhook handler example requires Flask:

```bash
pip install flask
```

## More Examples

For complete project templates with full setup (requirements.txt, .env, etc.), see the [developer-resources](https://github.com/rynko-dev/developer-resources) repository.
