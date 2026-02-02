"""
Rynko Python SDK

Official SDK for the Rynko document generation platform.

Example:
    >>> from rynko import Rynko
    >>>
    >>> client = Rynko(api_key="your_api_key")
    >>>
    >>> # Generate a PDF document
    >>> result = client.documents.generate(
    ...     template_id="tmpl_invoice",
    ...     format="pdf",
    ...     variables={"invoiceNumber": "INV-001"}
    ... )
    >>> print(f"Job ID: {result['jobId']}")
    >>> print(f"Download URL: {result['downloadUrl']}")
"""

from .client import Rynko, AsyncRynko
from .http import RetryConfig
from .exceptions import RynkoError, WebhookSignatureError
from .webhooks import verify_webhook_signature
from .types import (
    MetadataValue,
    DocumentMetadata,
    GenerateDocumentOptions,
    BatchDocument,
    GenerateBatchOptions,
    DocumentJobStatus,
    WebhookEventType,
    DocumentWebhookData,
    BatchWebhookData,
    WebhookEvent,
)

__version__ = "1.0.0"
__all__ = [
    # Client classes
    "Rynko",
    "AsyncRynko",
    "RetryConfig",
    # Exceptions
    "RynkoError",
    "WebhookSignatureError",
    # Utilities
    "verify_webhook_signature",
    # Types
    "MetadataValue",
    "DocumentMetadata",
    "GenerateDocumentOptions",
    "BatchDocument",
    "GenerateBatchOptions",
    "DocumentJobStatus",
    "WebhookEventType",
    "DocumentWebhookData",
    "BatchWebhookData",
    "WebhookEvent",
]
