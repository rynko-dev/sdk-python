"""
Extract Resource

Provides access to Rynko Extract for document data extraction,
schema discovery, and extraction configuration management.
"""

import json
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from ..http import HttpClient, AsyncHttpClient


# File can be a tuple of (filename, content, content_type) or (filename, content)
FileInput = Union[
    Tuple[str, bytes, str],
    Tuple[str, bytes],
    Tuple[str, Any],
    Tuple[str, Any, str],
]


def _prepare_files(files: Sequence[FileInput]) -> List[Tuple[str, Tuple[str, Any, str]]]:
    """Prepare files for multipart upload in httpx format."""
    result = []
    for f in files:
        if len(f) == 3:
            filename, content, content_type = f
            result.append(("files", (filename, content, content_type)))
        else:
            filename, content = f[0], f[1]
            result.append(("files", (filename, content, "application/octet-stream")))
    return result


def _prepare_data(
    *,
    schema: Optional[Dict[str, Any]] = None,
    schema_id: Optional[str] = None,
    gate_id: Optional[str] = None,
    instructions: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, str]:
    """Prepare form data fields, serializing dicts to JSON strings."""
    data: Dict[str, str] = {}
    if schema is not None:
        data["schema"] = json.dumps(schema)
    if schema_id is not None:
        data["schemaId"] = schema_id
    if gate_id is not None:
        data["gateId"] = gate_id
    if instructions is not None:
        data["instructions"] = instructions
    if metadata is not None:
        data["metadata"] = json.dumps(metadata)
    return data


class ExtractResource:
    """Synchronous Extract resource."""

    def __init__(self, http: HttpClient):
        self._http = http

    # ---- Jobs ----

    def create_job(
        self,
        *,
        files: Sequence[FileInput],
        schema: Optional[Dict[str, Any]] = None,
        schema_id: Optional[str] = None,
        gate_id: Optional[str] = None,
        instructions: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create an extraction job.

        Args:
            files: List of files to extract data from.
                Each file is a tuple of (filename, content, content_type) or
                (filename, content).
            schema: Optional JSON schema describing expected output structure
            schema_id: Optional saved schema/config ID to use
            gate_id: Optional Flow gate ID for validation
            instructions: Optional natural language extraction instructions
            metadata: Optional metadata for tracking

        Returns:
            Created extraction job

        Example:
            >>> with open("invoice.pdf", "rb") as f:
            ...     job = client.extract.create_job(
            ...         files=[("invoice.pdf", f.read(), "application/pdf")],
            ...         instructions="Extract invoice number, date, and line items",
            ...     )
            >>> print(f"Job ID: {job['id']}")
        """
        prepared_files = _prepare_files(files)
        data = _prepare_data(
            schema=schema,
            schema_id=schema_id,
            gate_id=gate_id,
            instructions=instructions,
            metadata=metadata,
        )

        response = self._http.post_multipart(
            "/api/extract/jobs",
            files=prepared_files,
            data=data or None,
        )
        return response.get("data", response)

    def get_job(self, job_id: str) -> Dict[str, Any]:
        """
        Get an extraction job by ID.

        Args:
            job_id: Extraction job ID

        Returns:
            Extraction job with status and results

        Example:
            >>> job = client.extract.get_job("ext_abc123")
            >>> if job["status"] == "completed":
            ...     print(job["result"])
        """
        response = self._http.get(f"/api/extract/jobs/{job_id}")
        return response.get("data", response)

    def list_jobs(
        self,
        *,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List extraction jobs.

        Args:
            status: Filter by status
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Dict with job list and pagination info

        Example:
            >>> result = client.extract.list_jobs(status="completed", limit=10)
            >>> for job in result.get("data", []):
            ...     print(f"{job['id']}: {job['status']}")
        """
        params: Dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset

        return self._http.get("/api/extract/jobs", params)

    def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """
        Cancel an extraction job.

        Args:
            job_id: Extraction job ID to cancel

        Returns:
            Cancellation confirmation

        Example:
            >>> client.extract.cancel_job("ext_abc123")
        """
        response = self._http.delete(f"/api/extract/jobs/{job_id}")
        return response.get("data", response)

    def get_usage(self) -> Dict[str, Any]:
        """
        Get extraction usage statistics.

        Returns:
            Usage data including credits consumed and remaining

        Example:
            >>> usage = client.extract.get_usage()
            >>> print(f"Used: {usage['used']}, Remaining: {usage['remaining']}")
        """
        response = self._http.get("/api/extract/usage")
        return response.get("data", response)

    # ---- Discovery ----

    def discover(
        self,
        *,
        files: Sequence[FileInput],
        instructions: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Discover schema from files using AI analysis.

        Args:
            files: List of files to analyze for schema discovery
            instructions: Optional instructions to guide discovery

        Returns:
            Discovered schema

        Example:
            >>> with open("invoice.pdf", "rb") as f:
            ...     schema = client.extract.discover(
            ...         files=[("invoice.pdf", f.read(), "application/pdf")],
            ...     )
            >>> print(schema)
        """
        prepared_files = _prepare_files(files)
        data: Dict[str, str] = {}
        if instructions is not None:
            data["instructions"] = instructions

        response = self._http.post_multipart(
            "/api/extract/discover",
            files=prepared_files,
            data=data or None,
        )
        return response.get("data", response)

    # ---- Configs ----

    def create_config(
        self,
        *,
        name: str,
        schema: Dict[str, Any],
        description: Optional[str] = None,
        instructions: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create an extraction config.

        Args:
            name: Config name
            schema: JSON schema for extraction
            description: Optional description
            instructions: Optional extraction instructions

        Returns:
            Created config

        Example:
            >>> config = client.extract.create_config(
            ...     name="Invoice Extractor",
            ...     schema={"type": "object", "properties": {...}},
            ...     instructions="Extract all invoice fields",
            ... )
            >>> print(f"Config ID: {config['id']}")
        """
        body: Dict[str, Any] = {"name": name, "schema": schema}
        if description is not None:
            body["description"] = description
        if instructions is not None:
            body["instructions"] = instructions

        response = self._http.post("/api/extract/configs", body)
        return response.get("data", response)

    def get_config(self, config_id: str) -> Dict[str, Any]:
        """
        Get an extraction config by ID.

        Args:
            config_id: Config ID

        Returns:
            Extraction config

        Example:
            >>> config = client.extract.get_config("cfg_abc123")
            >>> print(f"Name: {config['name']}")
        """
        response = self._http.get(f"/api/extract/configs/{config_id}")
        return response.get("data", response)

    def list_configs(
        self,
        *,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List extraction configs.

        Args:
            status: Filter by status
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Dict with config list and pagination info
        """
        params: Dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset

        return self._http.get("/api/extract/configs", params)

    def update_config(self, config_id: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Update an extraction config.

        Args:
            config_id: Config ID to update
            **kwargs: Config properties to update (name, schema, description, instructions)

        Returns:
            Updated config

        Example:
            >>> config = client.extract.update_config(
            ...     "cfg_abc123",
            ...     name="Updated Invoice Extractor",
            ... )
        """
        response = self._http.patch(f"/api/extract/configs/{config_id}", kwargs)
        return response.get("data", response)

    def delete_config(self, config_id: str) -> Dict[str, Any]:
        """
        Delete an extraction config.

        Args:
            config_id: Config ID to delete

        Returns:
            Deletion confirmation
        """
        response = self._http.delete(f"/api/extract/configs/{config_id}")
        return response.get("data", response)

    def publish_config(self, config_id: str) -> Dict[str, Any]:
        """
        Publish an extraction config.

        Args:
            config_id: Config ID to publish

        Returns:
            Published config

        Example:
            >>> config = client.extract.publish_config("cfg_abc123")
            >>> print(f"Status: {config['status']}")
        """
        response = self._http.post(f"/api/extract/configs/{config_id}/publish")
        return response.get("data", response)

    def get_config_versions(self, config_id: str) -> Dict[str, Any]:
        """
        Get version history for an extraction config.

        Args:
            config_id: Config ID

        Returns:
            List of config versions
        """
        return self._http.get(f"/api/extract/configs/{config_id}/versions")

    def restore_config_version(
        self, config_id: str, version_id: str
    ) -> Dict[str, Any]:
        """
        Restore an extraction config to a specific version.

        Args:
            config_id: Config ID
            version_id: Version ID to restore

        Returns:
            Restored config

        Example:
            >>> config = client.extract.restore_config_version("cfg_abc123", "ver_xyz")
        """
        response = self._http.post(
            f"/api/extract/configs/{config_id}/versions/{version_id}/restore"
        )
        return response.get("data", response)

    def run_config(
        self,
        config_id: str,
        *,
        files: Sequence[FileInput],
    ) -> Dict[str, Any]:
        """
        Run an extraction config on files.

        Args:
            config_id: Config ID to run
            files: List of files to extract data from

        Returns:
            Extraction job

        Example:
            >>> with open("invoice.pdf", "rb") as f:
            ...     job = client.extract.run_config(
            ...         "cfg_abc123",
            ...         files=[("invoice.pdf", f.read(), "application/pdf")],
            ...     )
        """
        prepared_files = _prepare_files(files)

        response = self._http.post_multipart(
            f"/api/extract/configs/{config_id}/run",
            files=prepared_files,
        )
        return response.get("data", response)

    # ---- Flow integration ----

    def extract_with_gate(
        self,
        gate_id: str,
        *,
        files: Sequence[FileInput],
        instructions: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extract data using a Flow gate for validation.

        Args:
            gate_id: Flow gate ID
            files: List of files to extract from
            instructions: Optional extraction instructions

        Returns:
            Extraction job with Flow validation

        Example:
            >>> with open("invoice.pdf", "rb") as f:
            ...     job = client.extract.extract_with_gate(
            ...         "gate_abc123",
            ...         files=[("invoice.pdf", f.read(), "application/pdf")],
            ...     )
        """
        prepared_files = _prepare_files(files)
        data: Dict[str, str] = {}
        if instructions is not None:
            data["instructions"] = instructions

        response = self._http.post_multipart(
            f"/api/flow/gates/{gate_id}/extract",
            files=prepared_files,
            data=data or None,
        )
        return response.get("data", response)

    def submit_file_run(
        self,
        gate_id: str,
        *,
        files: Sequence[FileInput],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Submit files to a Flow gate pipeline.

        Args:
            gate_id: Flow gate ID
            files: List of files to submit
            metadata: Optional metadata for tracking

        Returns:
            Flow run

        Example:
            >>> with open("document.pdf", "rb") as f:
            ...     run = client.extract.submit_file_run(
            ...         "gate_abc123",
            ...         files=[("document.pdf", f.read(), "application/pdf")],
            ...         metadata={"source": "upload"},
            ...     )
            >>> print(f"Run ID: {run['id']}")
        """
        prepared_files = _prepare_files(files)
        data: Dict[str, str] = {}
        if metadata is not None:
            data["metadata"] = json.dumps(metadata)

        response = self._http.post_multipart(
            f"/api/flow/gates/{gate_id}/runs/file",
            files=prepared_files,
            data=data or None,
        )
        return response.get("data", response)


class AsyncExtractResource:
    """Asynchronous Extract resource."""

    def __init__(self, http: AsyncHttpClient):
        self._http = http

    # ---- Jobs ----

    async def create_job(
        self,
        *,
        files: Sequence[FileInput],
        schema: Optional[Dict[str, Any]] = None,
        schema_id: Optional[str] = None,
        gate_id: Optional[str] = None,
        instructions: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create an extraction job (async)."""
        prepared_files = _prepare_files(files)
        data = _prepare_data(
            schema=schema,
            schema_id=schema_id,
            gate_id=gate_id,
            instructions=instructions,
            metadata=metadata,
        )

        response = await self._http.post_multipart(
            "/api/extract/jobs",
            files=prepared_files,
            data=data or None,
        )
        return response.get("data", response)

    async def get_job(self, job_id: str) -> Dict[str, Any]:
        """Get an extraction job by ID (async)."""
        response = await self._http.get(f"/api/extract/jobs/{job_id}")
        return response.get("data", response)

    async def list_jobs(
        self,
        *,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List extraction jobs (async)."""
        params: Dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset

        return await self._http.get("/api/extract/jobs", params)

    async def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """Cancel an extraction job (async)."""
        response = await self._http.delete(f"/api/extract/jobs/{job_id}")
        return response.get("data", response)

    async def get_usage(self) -> Dict[str, Any]:
        """Get extraction usage statistics (async)."""
        response = await self._http.get("/api/extract/usage")
        return response.get("data", response)

    # ---- Discovery ----

    async def discover(
        self,
        *,
        files: Sequence[FileInput],
        instructions: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Discover schema from files using AI analysis (async)."""
        prepared_files = _prepare_files(files)
        data: Dict[str, str] = {}
        if instructions is not None:
            data["instructions"] = instructions

        response = await self._http.post_multipart(
            "/api/extract/discover",
            files=prepared_files,
            data=data or None,
        )
        return response.get("data", response)

    # ---- Configs ----

    async def create_config(
        self,
        *,
        name: str,
        schema: Dict[str, Any],
        description: Optional[str] = None,
        instructions: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create an extraction config (async)."""
        body: Dict[str, Any] = {"name": name, "schema": schema}
        if description is not None:
            body["description"] = description
        if instructions is not None:
            body["instructions"] = instructions

        response = await self._http.post("/api/extract/configs", body)
        return response.get("data", response)

    async def get_config(self, config_id: str) -> Dict[str, Any]:
        """Get an extraction config by ID (async)."""
        response = await self._http.get(f"/api/extract/configs/{config_id}")
        return response.get("data", response)

    async def list_configs(
        self,
        *,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List extraction configs (async)."""
        params: Dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset

        return await self._http.get("/api/extract/configs", params)

    async def update_config(self, config_id: str, **kwargs: Any) -> Dict[str, Any]:
        """Update an extraction config (async)."""
        response = await self._http.patch(f"/api/extract/configs/{config_id}", kwargs)
        return response.get("data", response)

    async def delete_config(self, config_id: str) -> Dict[str, Any]:
        """Delete an extraction config (async)."""
        response = await self._http.delete(f"/api/extract/configs/{config_id}")
        return response.get("data", response)

    async def publish_config(self, config_id: str) -> Dict[str, Any]:
        """Publish an extraction config (async)."""
        response = await self._http.post(f"/api/extract/configs/{config_id}/publish")
        return response.get("data", response)

    async def get_config_versions(self, config_id: str) -> Dict[str, Any]:
        """Get version history for an extraction config (async)."""
        return await self._http.get(f"/api/extract/configs/{config_id}/versions")

    async def restore_config_version(
        self, config_id: str, version_id: str
    ) -> Dict[str, Any]:
        """Restore an extraction config to a specific version (async)."""
        response = await self._http.post(
            f"/api/extract/configs/{config_id}/versions/{version_id}/restore"
        )
        return response.get("data", response)

    async def run_config(
        self,
        config_id: str,
        *,
        files: Sequence[FileInput],
    ) -> Dict[str, Any]:
        """Run an extraction config on files (async)."""
        prepared_files = _prepare_files(files)

        response = await self._http.post_multipart(
            f"/api/extract/configs/{config_id}/run",
            files=prepared_files,
        )
        return response.get("data", response)

    # ---- Flow integration ----

    async def extract_with_gate(
        self,
        gate_id: str,
        *,
        files: Sequence[FileInput],
        instructions: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Extract data using a Flow gate for validation (async)."""
        prepared_files = _prepare_files(files)
        data: Dict[str, str] = {}
        if instructions is not None:
            data["instructions"] = instructions

        response = await self._http.post_multipart(
            f"/api/flow/gates/{gate_id}/extract",
            files=prepared_files,
            data=data or None,
        )
        return response.get("data", response)

    async def submit_file_run(
        self,
        gate_id: str,
        *,
        files: Sequence[FileInput],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Submit files to a Flow gate pipeline (async)."""
        prepared_files = _prepare_files(files)
        data: Dict[str, str] = {}
        if metadata is not None:
            data["metadata"] = json.dumps(metadata)

        response = await self._http.post_multipart(
            f"/api/flow/gates/{gate_id}/runs/file",
            files=prepared_files,
            data=data or None,
        )
        return response.get("data", response)
