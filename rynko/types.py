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


# ============================================
# Flow Types
# ============================================

FlowRunStatus = Literal[
    "pending",
    "validating",
    "approved",
    "rejected",
    "review_required",
    "completed",
    "delivered",
    "validation_failed",
    "render_failed",
    "delivery_failed",
]

FLOW_RUN_TERMINAL_STATUSES = frozenset({
    "completed",
    "delivered",
    "approved",
    "rejected",
    "validation_failed",
    "render_failed",
    "delivery_failed",
})


class FlowGate(TypedDict, total=False):
    """A Flow gate for validating AI outputs."""
    id: str
    name: str
    slug: Optional[str]
    description: Optional[str]
    status: Literal["draft", "published", "archived"]
    schema_version: Optional[int]
    created_at: str
    updated_at: str


class FlowValidationError(TypedDict, total=False):
    """A validation error from a Flow run."""
    field: Optional[str]
    rule: Optional[str]
    message: str


class FlowRun(TypedDict, total=False):
    """A Flow run representing a validation submission."""
    id: str
    gate_id: str
    status: FlowRunStatus
    input: Dict[str, Any]
    output: Optional[Dict[str, Any]]
    errors: Optional[List[FlowValidationError]]
    metadata: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str
    completed_at: Optional[str]


class FlowApproval(TypedDict, total=False):
    """A Flow approval for human review."""
    id: str
    run_id: str
    gate_id: str
    status: Literal["pending", "approved", "rejected"]
    reviewer_email: Optional[str]
    reviewer_note: Optional[str]
    created_at: str
    updated_at: str
    resolved_at: Optional[str]


class FlowDelivery(TypedDict, total=False):
    """A Flow delivery representing a webhook delivery attempt."""
    id: str
    run_id: str
    status: Literal["pending", "delivered", "failed"]
    url: Optional[str]
    http_status: Optional[int]
    attempts: int
    last_attempt_at: Optional[str]
    error: Optional[str]
    created_at: str


class SubmitRunOptions(TypedDict, total=False):
    """Options for submitting a Flow run."""
    input: Dict[str, Any]
    metadata: Optional[Dict[str, Any]]
    webhook_url: Optional[str]


class ListGatesOptions(TypedDict, total=False):
    status: Optional[Literal["draft", "published", "archived"]]
    limit: Optional[int]
    page: Optional[int]


class ListRunsOptions(TypedDict, total=False):
    status: Optional[FlowRunStatus]
    limit: Optional[int]
    page: Optional[int]


class ListApprovalsOptions(TypedDict, total=False):
    status: Optional[Literal["pending", "approved", "rejected"]]
    limit: Optional[int]
    page: Optional[int]
