"""
Rynko SDK Type Definitions
"""

from typing import Any, Dict, List, Literal, Optional, TypedDict, Union


# Metadata Types
# Metadata must be a flat object with string, number, boolean, or null values
MetadataValue = Union[str, int, float, bool, None]
DocumentMetadata = Dict[str, MetadataValue]


# Document Types
class GenerateDocumentOptions(TypedDict, total=False):
    """Options for generating a single document."""
    template_id: str
    format: Literal["pdf", "excel"]
    variables: Optional[Dict[str, Any]]
    workspace_id: Optional[str]
    filename: Optional[str]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]
    use_draft: Optional[bool]
    use_credit: Optional[bool]
    metadata: Optional[DocumentMetadata]
    """
    Custom metadata for tracking and correlation.
    Must be a flat object (no nested objects). Max size: 10KB.
    Returned in job status and webhook payloads.
    Example: {"orderId": "ord_123", "customerId": "cust_456"}
    """


class BatchDocument(TypedDict, total=False):
    """Document specification for batch generation."""
    variables: Optional[Dict[str, Any]]
    filename: Optional[str]
    metadata: Optional[DocumentMetadata]
    """Per-document metadata."""


class GenerateBatchOptions(TypedDict, total=False):
    """Options for generating multiple documents in a batch."""
    template_id: str
    format: Literal["pdf", "excel"]
    documents: List[BatchDocument]
    workspace_id: Optional[str]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]
    use_draft: Optional[bool]
    use_credit: Optional[bool]
    metadata: Optional[DocumentMetadata]
    """
    Batch-level metadata (applies to the entire batch).
    Must be a flat object (no nested objects). Max size: 10KB.
    """


DocumentJobStatus = Literal["queued", "processing", "completed", "failed"]

WebhookEventType = Literal[
    "document.generated",
    "document.downloaded",
    "document.failed",
    "batch.completed",
]


# Webhook Event Data Types
class DocumentWebhookData(TypedDict, total=False):
    """Data payload for document webhook events."""
    job_id: str
    status: DocumentJobStatus
    template_id: str
    format: Literal["pdf", "excel"]
    download_url: Optional[str]
    file_size: Optional[int]
    error_message: Optional[str]
    error_code: Optional[str]
    metadata: Optional[DocumentMetadata]
    """Custom metadata passed in the generate request."""


class BatchWebhookData(TypedDict, total=False):
    """Data payload for batch webhook events."""
    batch_id: str
    status: str
    template_id: str
    format: Literal["pdf", "excel"]
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    metadata: Optional[DocumentMetadata]
    """Custom metadata passed in the batch request."""


class WebhookEvent(TypedDict):
    """Webhook event payload."""
    id: str
    type: WebhookEventType
    timestamp: str
    data: Union[DocumentWebhookData, BatchWebhookData]


class CreateWebhookOptions(TypedDict, total=False):
    url: str
    events: List[WebhookEventType]
    name: Optional[str]


class ListDocumentJobsOptions(TypedDict, total=False):
    status: Optional[DocumentJobStatus]
    format: Optional[Literal["pdf", "excel"]]
    template_id: Optional[str]
    workspace_id: Optional[str]
    date_from: Optional[str]
    date_to: Optional[str]
    limit: Optional[int]
    page: Optional[int]


class ListTemplatesOptions(TypedDict, total=False):
    type: Optional[Literal["pdf", "excel"]]
    limit: Optional[int]
    page: Optional[int]
