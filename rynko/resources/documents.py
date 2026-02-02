"""
Documents Resource
"""

import asyncio
import time
from typing import Any, Dict, List, Optional

from ..http import HttpClient, AsyncHttpClient


class DocumentsResource:
    """Synchronous documents resource."""

    def __init__(self, http: HttpClient):
        self._http = http

    def generate(
        self,
        template_id: str,
        format: str,
        *,
        variables: Optional[Dict[str, Any]] = None,
        filename: Optional[str] = None,
        webhook_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        use_draft: bool = False,
        use_credit: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate a document from a template.

        This is an async operation - the document is queued for generation.
        Use wait_for_completion() to poll until ready.

        Args:
            template_id: Template ID to use
            format: Output format ('pdf', 'excel', or 'csv')
            variables: Template variables for content generation
            filename: Custom filename (without extension)
            webhook_url: Webhook URL to receive completion notification
            metadata: Custom metadata to pass through to webhook
            use_draft: Use draft version instead of published version
            use_credit: Force use of purchased credits instead of free quota

        Returns:
            Document job with jobId, status, statusUrl, estimatedWaitSeconds

        Example:
            >>> job = client.documents.generate(
            ...     template_id="tmpl_invoice",
            ...     format="pdf",
            ...     variables={
            ...         "customerName": "John Doe",
            ...         "invoiceNumber": "INV-001",
            ...         "amount": 150.00,
            ...     },
            ...     # Optional: attach metadata for tracking
            ...     metadata={
            ...         "orderId": "ord_12345",
            ...         "customerId": "cust_67890",
            ...     }
            ... )
            >>> print(f"Job ID: {job['jobId']}")
            >>> # Wait for completion to get download URL
            >>> completed = client.documents.wait_for_completion(job["jobId"])
            >>> print(f"Download URL: {completed['downloadUrl']}")
            >>> # Metadata is returned in job status and webhook payloads
            >>> print(f"Metadata: {completed.get('metadata')}")
        """
        body: Dict[str, Any] = {
            "templateId": template_id,
            "format": format,
        }

        if variables:
            body["variables"] = variables
        if filename:
            body["filename"] = filename
        if webhook_url:
            body["webhookUrl"] = webhook_url
        if metadata:
            body["metadata"] = metadata
        if use_draft:
            body["useDraft"] = use_draft
        if use_credit:
            body["useCredit"] = use_credit

        response = self._http.post("/api/v1/documents/generate", body)
        return response.get("data", response)

    def generate_pdf(
        self,
        template_id: str,
        *,
        variables: Optional[Dict[str, Any]] = None,
        filename: Optional[str] = None,
        webhook_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        use_draft: bool = False,
        use_credit: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate a PDF document from a template.

        Example:
            >>> job = client.documents.generate_pdf(
            ...     template_id="tmpl_invoice",
            ...     variables={"invoiceNumber": "INV-001"}
            ... )
            >>> completed = client.documents.wait_for_completion(job["jobId"])
        """
        return self.generate(
            template_id=template_id,
            format="pdf",
            variables=variables,
            filename=filename,
            webhook_url=webhook_url,
            metadata=metadata,
            use_draft=use_draft,
            use_credit=use_credit,
        )

    def generate_excel(
        self,
        template_id: str,
        *,
        variables: Optional[Dict[str, Any]] = None,
        filename: Optional[str] = None,
        webhook_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        use_draft: bool = False,
        use_credit: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate an Excel document from a template.

        Example:
            >>> job = client.documents.generate_excel(
            ...     template_id="tmpl_report",
            ...     variables={"reportDate": "2025-01-15"}
            ... )
            >>> completed = client.documents.wait_for_completion(job["jobId"])
        """
        return self.generate(
            template_id=template_id,
            format="excel",
            variables=variables,
            filename=filename,
            webhook_url=webhook_url,
            metadata=metadata,
            use_draft=use_draft,
            use_credit=use_credit,
        )

    def generate_batch(
        self,
        template_id: str,
        format: str,
        documents: List[Dict[str, Any]],
        *,
        webhook_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        use_draft: bool = False,
        use_credit: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate multiple documents in a batch.

        This is an async operation - documents are queued for generation.

        Args:
            template_id: Template ID to use
            format: Output format ('pdf', 'excel', or 'csv')
            documents: List of variable sets (one dict per document)
            webhook_url: Webhook URL to receive batch completion notification
            metadata: Custom metadata for the batch
            use_draft: Use draft version instead of published version
            use_credit: Force use of purchased credits instead of free quota

        Returns:
            Batch info with batchId, status, totalJobs, statusUrl, estimatedWaitSeconds

        Example:
            >>> batch = client.documents.generate_batch(
            ...     template_id="tmpl_invoice",
            ...     format="pdf",
            ...     # Optional: batch-level metadata
            ...     metadata={
            ...         "batchRunId": "run_20250115",
            ...         "triggeredBy": "scheduled_job",
            ...     },
            ...     documents=[
            ...         # Each document can have its own variables and metadata
            ...         {"variables": {"invoiceNumber": "INV-001"}, "metadata": {"rowNumber": 1}},
            ...         {"variables": {"invoiceNumber": "INV-002"}, "metadata": {"rowNumber": 2}},
            ...     ]
            ... )
            >>> print(f"Batch ID: {batch['batchId']}")
            >>> print(f"Total jobs: {batch['totalJobs']}")
        """
        body: Dict[str, Any] = {
            "templateId": template_id,
            "format": format,
            "documents": documents,
        }

        if webhook_url:
            body["webhookUrl"] = webhook_url
        if metadata:
            body["metadata"] = metadata
        if use_draft:
            body["useDraft"] = use_draft
        if use_credit:
            body["useCredit"] = use_credit

        response = self._http.post("/api/v1/documents/generate/batch", body)
        return response.get("data", response)

    def get_job(self, job_id: str) -> Dict[str, Any]:
        """
        Get a document job by ID.

        Example:
            >>> job = client.documents.get_job("job_abc123")
            >>> if job["status"] == "completed":
            ...     print(f"Download: {job['downloadUrl']}")
        """
        response = self._http.get(f"/api/v1/documents/jobs/{job_id}")
        return response.get("data", response)

    def list_jobs(
        self,
        *,
        status: Optional[str] = None,
        template_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: int = 20,
        page: int = 1,
    ) -> Dict[str, Any]:
        """
        List document jobs with optional filters.

        Returns:
            Dict with 'data' (list) and 'meta' (pagination)

        Example:
            >>> result = client.documents.list_jobs(
            ...     status="completed",
            ...     limit=10
            ... )
            >>> print(f"Found {result['meta']['total']} jobs")
        """
        offset = (page - 1) * limit
        params = {
            "status": status,
            "templateId": template_id,
            "workspaceId": workspace_id,
            "limit": limit,
            "offset": offset,
        }
        # Backend returns { jobs: [], total: number }
        response = self._http.get("/api/v1/documents/jobs", params)

        # Normalize to { data: [], meta: {} } format
        jobs = response.get("jobs", response.get("data", []))
        total = response.get("total", len(jobs))

        return {
            "data": jobs,
            "meta": {
                "total": total,
                "page": page,
                "limit": limit,
                "totalPages": (total + limit - 1) // limit if limit > 0 else 1,
            },
        }

    def wait_for_completion(
        self,
        job_id: str,
        *,
        poll_interval: float = 1.0,
        timeout: float = 30.0,
    ) -> Dict[str, Any]:
        """
        Wait for a document job to complete.

        Args:
            job_id: Job ID to wait for
            poll_interval: Time between polls in seconds (default: 1.0)
            timeout: Maximum wait time in seconds (default: 30.0)

        Returns:
            Completed job with downloadUrl

        Raises:
            TimeoutError: If job doesn't complete within timeout

        Example:
            >>> result = client.documents.generate(
            ...     template_id="tmpl_invoice",
            ...     format="pdf",
            ...     variables={"invoiceNumber": "INV-001"}
            ... )
            >>> completed = client.documents.wait_for_completion(result["jobId"])
            >>> print(f"Download: {completed['downloadUrl']}")
        """
        start_time = time.time()

        while True:
            job = self.get_job(job_id)

            if job["status"] in ("completed", "failed"):
                return job

            if time.time() - start_time > timeout:
                raise TimeoutError(f"Timeout waiting for job {job_id} to complete")

            time.sleep(poll_interval)


class AsyncDocumentsResource:
    """Asynchronous documents resource."""

    def __init__(self, http: AsyncHttpClient):
        self._http = http

    async def generate(
        self,
        template_id: str,
        format: str,
        *,
        variables: Optional[Dict[str, Any]] = None,
        filename: Optional[str] = None,
        webhook_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        use_draft: bool = False,
        use_credit: bool = False,
    ) -> Dict[str, Any]:
        """Generate a document from a template (async)."""
        body: Dict[str, Any] = {
            "templateId": template_id,
            "format": format,
        }

        if variables:
            body["variables"] = variables
        if filename:
            body["filename"] = filename
        if webhook_url:
            body["webhookUrl"] = webhook_url
        if metadata:
            body["metadata"] = metadata
        if use_draft:
            body["useDraft"] = use_draft
        if use_credit:
            body["useCredit"] = use_credit

        response = await self._http.post("/api/v1/documents/generate", body)
        return response.get("data", response)

    async def generate_pdf(
        self,
        template_id: str,
        *,
        variables: Optional[Dict[str, Any]] = None,
        filename: Optional[str] = None,
        webhook_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        use_draft: bool = False,
        use_credit: bool = False,
    ) -> Dict[str, Any]:
        """Generate a PDF document from a template (async)."""
        return await self.generate(
            template_id=template_id,
            format="pdf",
            variables=variables,
            filename=filename,
            webhook_url=webhook_url,
            metadata=metadata,
            use_draft=use_draft,
            use_credit=use_credit,
        )

    async def generate_excel(
        self,
        template_id: str,
        *,
        variables: Optional[Dict[str, Any]] = None,
        filename: Optional[str] = None,
        webhook_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        use_draft: bool = False,
        use_credit: bool = False,
    ) -> Dict[str, Any]:
        """Generate an Excel document from a template (async)."""
        return await self.generate(
            template_id=template_id,
            format="excel",
            variables=variables,
            filename=filename,
            webhook_url=webhook_url,
            metadata=metadata,
            use_draft=use_draft,
            use_credit=use_credit,
        )

    async def generate_batch(
        self,
        template_id: str,
        format: str,
        documents: List[Dict[str, Any]],
        *,
        webhook_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        use_draft: bool = False,
        use_credit: bool = False,
    ) -> Dict[str, Any]:
        """Generate multiple documents in a batch (async)."""
        body: Dict[str, Any] = {
            "templateId": template_id,
            "format": format,
            "documents": documents,
        }

        if webhook_url:
            body["webhookUrl"] = webhook_url
        if metadata:
            body["metadata"] = metadata
        if use_draft:
            body["useDraft"] = use_draft
        if use_credit:
            body["useCredit"] = use_credit

        response = await self._http.post("/api/v1/documents/generate/batch", body)
        return response.get("data", response)

    async def get_job(self, job_id: str) -> Dict[str, Any]:
        """Get a document job by ID (async)."""
        response = await self._http.get(f"/api/v1/documents/jobs/{job_id}")
        return response.get("data", response)

    async def list_jobs(
        self,
        *,
        status: Optional[str] = None,
        template_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: int = 20,
        page: int = 1,
    ) -> Dict[str, Any]:
        """List document jobs with optional filters (async)."""
        offset = (page - 1) * limit
        params = {
            "status": status,
            "templateId": template_id,
            "workspaceId": workspace_id,
            "limit": limit,
            "offset": offset,
        }
        # Backend returns { jobs: [], total: number }
        response = await self._http.get("/api/v1/documents/jobs", params)

        # Normalize to { data: [], meta: {} } format
        jobs = response.get("jobs", response.get("data", []))
        total = response.get("total", len(jobs))

        return {
            "data": jobs,
            "meta": {
                "total": total,
                "page": page,
                "limit": limit,
                "totalPages": (total + limit - 1) // limit if limit > 0 else 1,
            },
        }

    async def wait_for_completion(
        self,
        job_id: str,
        *,
        poll_interval: float = 1.0,
        timeout: float = 30.0,
    ) -> Dict[str, Any]:
        """
        Wait for a document job to complete (async).

        Args:
            job_id: Job ID to wait for
            poll_interval: Time between polls in seconds (default: 1.0)
            timeout: Maximum wait time in seconds (default: 30.0)

        Returns:
            Completed job with downloadUrl

        Raises:
            TimeoutError: If job doesn't complete within timeout
        """
        start_time = time.time()

        while True:
            job = await self.get_job(job_id)

            if job["status"] in ("completed", "failed"):
                return job

            if time.time() - start_time > timeout:
                raise TimeoutError(f"Timeout waiting for job {job_id} to complete")

            await asyncio.sleep(poll_interval)
