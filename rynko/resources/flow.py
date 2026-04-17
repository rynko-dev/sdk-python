"""
Flow Resource
"""

import asyncio
import time
from typing import Any, Dict, List, Optional


from ..http import HttpClient, AsyncHttpClient

TERMINAL_STATUSES = frozenset({
    "validated",
    "completed",
    "delivered",
    "approved",
    "rejected",
    "validation_failed",
    "render_failed",
    "delivery_failed",
})


class FlowResource:
    """Synchronous Flow resource."""

    def __init__(self, http: HttpClient):
        self._http = http

    # ---- Gates ----

    def create_gate(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        workspace_id: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        rules: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Create a new gate.

        Args:
            name: Gate name
            description: Optional gate description
            workspace_id: Optional workspace ID
            schema: Optional JSON schema for validation
            rules: Optional list of validation rules
            **kwargs: Additional gate properties

        Returns:
            Created gate

        Example:
            >>> gate = client.flow.create_gate(
            ...     name="Order Validation",
            ...     schema={"type": "object", "properties": {...}},
            ... )
            >>> print(f"Gate ID: {gate['id']}")
        """
        body: Dict[str, Any] = {"name": name, **kwargs}
        if description is not None:
            body["description"] = description
        if workspace_id is not None:
            body["workspaceId"] = workspace_id
        if schema is not None:
            body["schema"] = schema
        if rules is not None:
            body["rules"] = rules

        return self._http.post("/api/flow/gates", body)

    def update_gate(self, gate_id: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Update a gate.

        Args:
            gate_id: Gate ID to update
            **kwargs: Gate properties to update (name, description, rules, etc.)

        Returns:
            Updated gate

        Example:
            >>> gate = client.flow.update_gate(
            ...     "gate_abc123",
            ...     name="Updated Gate Name",
            ...     description="New description",
            ... )
        """
        return self._http.put(f"/api/flow/gates/{gate_id}", kwargs)

    def delete_gate(self, gate_id: str) -> Dict[str, Any]:
        """
        Delete a gate.

        Args:
            gate_id: Gate ID to delete

        Returns:
            Deletion confirmation

        Example:
            >>> client.flow.delete_gate("gate_abc123")
        """
        return self._http.delete(f"/api/flow/gates/{gate_id}")

    def update_gate_schema(
        self,
        gate_id: str,
        *,
        schema: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Update a gate's schema.

        Args:
            gate_id: Gate ID
            schema: New JSON schema

        Returns:
            Updated gate

        Example:
            >>> client.flow.update_gate_schema(
            ...     "gate_abc123",
            ...     schema={"type": "object", "properties": {...}},
            ... )
        """
        return self._http.put(f"/api/flow/gates/{gate_id}/schema", {"schema": schema})

    def publish_gate(self, gate_id: str) -> Dict[str, Any]:
        """
        Publish a gate, making it available for validation runs.

        Args:
            gate_id: Gate ID to publish

        Returns:
            Published gate

        Example:
            >>> gate = client.flow.publish_gate("gate_abc123")
            >>> print(f"Status: {gate['status']}")  # 'published'
        """
        return self._http.post(f"/api/flow/gates/{gate_id}/publish")

    def rollback_gate(
        self,
        gate_id: str,
        *,
        version_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Rollback a gate to a previous version.

        Args:
            gate_id: Gate ID to rollback
            version_id: Optional specific version ID to rollback to

        Returns:
            Rolled-back gate

        Example:
            >>> gate = client.flow.rollback_gate("gate_abc123")
        """
        body: Dict[str, Any] = {}
        if version_id is not None:
            body["versionId"] = version_id

        return self._http.post(f"/api/flow/gates/{gate_id}/rollback", body)

    def export_gate(self, gate_id: str) -> Dict[str, Any]:
        """
        Export a gate configuration.

        Args:
            gate_id: Gate ID to export

        Returns:
            Gate configuration data for import

        Example:
            >>> config = client.flow.export_gate("gate_abc123")
            >>> # Save or import to another environment
        """
        return self._http.get(f"/api/flow/gates/{gate_id}/export")

    def import_gate(self, *, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Import a gate from exported configuration.

        Args:
            data: Gate configuration data from export_gate()

        Returns:
            Imported gate

        Example:
            >>> config = client.flow.export_gate("gate_abc123")
            >>> imported = client.flow.import_gate(data=config)
            >>> print(f"New gate ID: {imported['id']}")
        """
        return self._http.post("/api/flow/gates/import", data)

    def test_gate(
        self,
        gate_id: str,
        *,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Test a gate with a payload (dry-run validation, no run created).

        Args:
            gate_id: Gate ID to test
            payload: Test payload to validate

        Returns:
            Validation result without creating a run

        Example:
            >>> result = client.flow.test_gate(
            ...     "gate_abc123",
            ...     payload={"name": "John", "amount": 150.00},
            ... )
            >>> print(f"Valid: {result.get('valid')}")
        """
        return self._http.post(
            f"/api/flow/gates/{gate_id}/test", {"payload": payload}
        )

    def validate_gate(
        self,
        gate_id: str,
        *,
        payload: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        webhook_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Validate a payload against a gate (creates a run with validation_id).

        Args:
            gate_id: Gate ID to validate against
            payload: Data to validate
            metadata: Optional metadata for tracking
            webhook_url: Optional webhook URL for notifications

        Returns:
            Validation result with validation_id

        Example:
            >>> result = client.flow.validate_gate(
            ...     "gate_abc123",
            ...     payload={"name": "John", "amount": 150.00},
            ... )
            >>> print(f"Validation ID: {result['validationId']}")
        """
        body: Dict[str, Any] = {"payload": payload}
        if metadata is not None:
            body["metadata"] = metadata
        if webhook_url is not None:
            body["webhookUrl"] = webhook_url

        return self._http.post(f"/api/flow/gates/{gate_id}/validate", body)

    def verify_validation(
        self,
        *,
        validation_id: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Verify a validation result.

        Args:
            validation_id: Validation ID from validate_gate()
            payload: Original payload to verify

        Returns:
            Verification result

        Example:
            >>> result = client.flow.verify_validation(
            ...     validation_id="val_abc123",
            ...     payload={"name": "John", "amount": 150.00},
            ... )
        """
        return self._http.post(
            "/api/flow/verify",
            {"validationId": validation_id, "payload": payload},
        )

    def get_run_payload(
        self,
        run_id: str,
        *,
        field: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get the payload for a run.

        Args:
            run_id: Run ID
            field: Optional specific field to retrieve

        Returns:
            Run payload data

        Example:
            >>> payload = client.flow.get_run_payload("run_abc123")
            >>> print(payload)
        """
        params: Dict[str, Any] = {}
        if field is not None:
            params["field"] = field

        return self._http.get(f"/api/flow/runs/{run_id}/payload", params)

    def get_run_chain(self, correlation_id: str) -> Dict[str, Any]:
        """
        Get a chain of runs by correlation ID.

        Args:
            correlation_id: Correlation ID linking related runs

        Returns:
            Chain of related runs

        Example:
            >>> chain = client.flow.get_run_chain("corr_abc123")
            >>> for run in chain.get("runs", []):
            ...     print(f"{run['id']}: {run['status']}")
        """
        return self._http.get(f"/api/flow/runs/chain/{correlation_id}")

    def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """
        Get a transaction by ID.

        Args:
            transaction_id: Transaction ID

        Returns:
            Transaction details

        Example:
            >>> txn = client.flow.get_transaction("txn_abc123")
            >>> print(f"Status: {txn['status']}")
        """
        return self._http.get(f"/api/flow/transactions/{transaction_id}")

    def list_gates(
        self,
        *,
        status: Optional[str] = None,
        limit: int = 20,
        page: int = 1,
    ) -> Dict[str, Any]:
        """
        List all gates.

        Returns:
            Dict with 'data' (list) and 'meta' (pagination)

        Example:
            >>> result = client.flow.list_gates(status="published")
            >>> for gate in result["data"]:
            ...     print(gate["name"], gate["status"])
        """
        params: Dict[str, Any] = {"limit": limit, "page": page}
        if status:
            params["status"] = status

        response = self._http.get("/api/flow/gates", params)
        return self._paginate(response, "gates", page, limit)

    def get_gate(self, gate_id: str) -> Dict[str, Any]:
        """
        Get a gate by ID.

        Example:
            >>> gate = client.flow.get_gate("gate_abc123")
            >>> print(gate["name"])
        """
        return self._http.get(f"/api/flow/gates/{gate_id}")

    # ---- Runs ----

    def submit_run(
        self,
        gate_id: str,
        *,
        input: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        webhook_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Submit a run to a gate for validation.

        Args:
            gate_id: Gate ID to submit to
            input: Input data to validate against the gate schema
            metadata: Optional metadata for tracking
            webhook_url: Webhook URL for run completion notification

        Returns:
            Run with id, status, gateId, createdAt

        Example:
            >>> run = client.flow.submit_run(
            ...     "gate_abc123",
            ...     input={"name": "John Doe", "amount": 150.00},
            ...     metadata={"source": "checkout"},
            ... )
            >>> print(f"Run ID: {run['id']}")
            >>> result = client.flow.wait_for_run(run["id"])
            >>> print(f"Status: {result['status']}")
        """
        body: Dict[str, Any] = {"payload": input}
        if metadata:
            body["metadata"] = metadata
        if webhook_url:
            body["webhookUrl"] = webhook_url

        response = self._http.post(f"/api/flow/gates/{gate_id}/runs", body)
        # Map runId → id for consistency with get_run/list_runs
        if "runId" in response and "id" not in response:
            response["id"] = response["runId"]
        return response

    def get_run(self, run_id: str) -> Dict[str, Any]:
        """
        Get a run by ID.

        Example:
            >>> run = client.flow.get_run("run_abc123")
            >>> if run["status"] == "approved":
            ...     print("Run approved!", run.get("output"))
        """
        return self._http.get(f"/api/flow/runs/{run_id}")

    def list_runs(
        self,
        *,
        status: Optional[str] = None,
        limit: int = 20,
        page: int = 1,
    ) -> Dict[str, Any]:
        """
        List all runs.

        Returns:
            Dict with 'data' (list) and 'meta' (pagination)
        """
        params: Dict[str, Any] = {"limit": limit, "page": page}
        if status:
            params["status"] = status

        response = self._http.get("/api/flow/runs", params)
        return self._paginate(response, "runs", page, limit)

    def list_runs_by_gate(
        self,
        gate_id: str,
        *,
        status: Optional[str] = None,
        limit: int = 20,
        page: int = 1,
    ) -> Dict[str, Any]:
        """
        List runs for a specific gate.

        Returns:
            Dict with 'data' (list) and 'meta' (pagination)
        """
        params: Dict[str, Any] = {"limit": limit, "page": page}
        if status:
            params["status"] = status

        response = self._http.get(f"/api/flow/gates/{gate_id}/runs", params)
        return self._paginate(response, "runs", page, limit)

    def list_active_runs(
        self,
        *,
        limit: int = 20,
        page: int = 1,
    ) -> Dict[str, Any]:
        """
        List active (non-terminal) runs.

        Returns:
            Dict with 'data' (list) and 'meta' (pagination)
        """
        params: Dict[str, Any] = {"limit": limit, "page": page}

        response = self._http.get("/api/flow/runs/active", params)
        return self._paginate(response, "runs", page, limit)

    def wait_for_run(
        self,
        run_id: str,
        *,
        poll_interval: float = 1.0,
        timeout: float = 60.0,
    ) -> Dict[str, Any]:
        """
        Wait for a run to reach a terminal state.

        Args:
            run_id: Run ID to wait for
            poll_interval: Time between polls in seconds (default: 1.0)
            timeout: Maximum wait time in seconds (default: 60.0)

        Returns:
            Completed run

        Raises:
            TimeoutError: If run doesn't complete within timeout

        Example:
            >>> run = client.flow.submit_run("gate_abc123", input={"name": "John"})
            >>> result = client.flow.wait_for_run(run["id"], timeout=120.0)
            >>> if result["status"] == "approved":
            ...     print("Approved!", result.get("output"))
        """
        start_time = time.time()

        while True:
            run = self.get_run(run_id)

            if run["status"] in TERMINAL_STATUSES:
                return run

            if time.time() - start_time > timeout:
                raise TimeoutError(f"Timeout waiting for run {run_id} to complete")

            time.sleep(poll_interval)

    # ---- Approvals ----

    def list_approvals(
        self,
        *,
        status: Optional[str] = None,
        limit: int = 20,
        page: int = 1,
    ) -> Dict[str, Any]:
        """
        List approvals.

        Returns:
            Dict with 'data' (list) and 'meta' (pagination)

        Example:
            >>> result = client.flow.list_approvals(status="pending")
            >>> for approval in result["data"]:
            ...     print(f"Approval {approval['id']} for run {approval['runId']}")
        """
        params: Dict[str, Any] = {"limit": limit, "page": page}
        if status:
            params["status"] = status

        response = self._http.get("/api/flow/approvals", params)
        return self._paginate(response, "approvals", page, limit)

    def approve(
        self,
        approval_id: str,
        *,
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Approve a pending approval.

        Example:
            >>> approval = client.flow.approve("approval_abc123", note="Looks good")
        """
        body: Dict[str, Any] = {}
        if note:
            body["note"] = note

        return self._http.post(f"/api/flow/approvals/{approval_id}/approve", body)

    def reject(
        self,
        approval_id: str,
        *,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Reject a pending approval.

        Example:
            >>> approval = client.flow.reject("approval_abc123", reason="Invalid amount")
        """
        body: Dict[str, Any] = {}
        if reason:
            body["reason"] = reason

        return self._http.post(f"/api/flow/approvals/{approval_id}/reject", body)

    def resend_approval_email(self, run_id: str) -> Dict[str, Any]:
        """
        Resend approval notification emails for a run.

        Re-sends approval request emails to all pending approvers for a run
        that is in ``review_required`` status.

        Example:
            >>> result = client.flow.resend_approval_email("run_abc123")
            >>> print(f"Sent {result['sentCount']} of {result['totalApprovers']} emails")
        """
        return self._http.post(f"/api/flow/approvals/resend/{run_id}", {})

    # ---- Deliveries ----

    def list_deliveries(
        self,
        run_id: str,
        *,
        limit: int = 20,
        page: int = 1,
    ) -> Dict[str, Any]:
        """
        List deliveries for a run.

        Returns:
            Dict with 'data' (list) and 'meta' (pagination)
        """
        params: Dict[str, Any] = {"limit": limit, "page": page}

        response = self._http.get(f"/api/flow/runs/{run_id}/deliveries", params)
        return self._paginate(response, "deliveries", page, limit)

    def retry_delivery(self, delivery_id: str) -> Dict[str, Any]:
        """
        Retry a failed delivery.

        Example:
            >>> delivery = client.flow.retry_delivery("delivery_abc123")
            >>> print(f"Retry status: {delivery['status']}")
        """
        return self._http.post(f"/api/flow/deliveries/{delivery_id}/retry", {})

    # ---- Helpers ----

    @staticmethod
    def _paginate(
        response: Dict[str, Any], key: str, page: int, limit: int
    ) -> Dict[str, Any]:
        data = response.get("data", response.get(key, []))
        total = response.get("total", response.get("meta", {}).get("total", len(data)))

        return {
            "data": data,
            "meta": {
                "total": total,
                "page": page,
                "limit": limit,
                "totalPages": (total + limit - 1) // limit if limit > 0 else 1,
            },
        }


class AsyncFlowResource:
    """Asynchronous Flow resource."""

    def __init__(self, http: AsyncHttpClient):
        self._http = http

    # ---- Gates ----

    async def create_gate(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        workspace_id: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        rules: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Create a new gate (async)."""
        body: Dict[str, Any] = {"name": name, **kwargs}
        if description is not None:
            body["description"] = description
        if workspace_id is not None:
            body["workspaceId"] = workspace_id
        if schema is not None:
            body["schema"] = schema
        if rules is not None:
            body["rules"] = rules

        return await self._http.post("/api/flow/gates", body)

    async def update_gate(self, gate_id: str, **kwargs: Any) -> Dict[str, Any]:
        """Update a gate (async)."""
        return await self._http.put(f"/api/flow/gates/{gate_id}", kwargs)

    async def delete_gate(self, gate_id: str) -> Dict[str, Any]:
        """Delete a gate (async)."""
        return await self._http.delete(f"/api/flow/gates/{gate_id}")

    async def update_gate_schema(
        self,
        gate_id: str,
        *,
        schema: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a gate's schema (async)."""
        return await self._http.put(
            f"/api/flow/gates/{gate_id}/schema", {"schema": schema}
        )

    async def publish_gate(self, gate_id: str) -> Dict[str, Any]:
        """Publish a gate (async)."""
        return await self._http.post(f"/api/flow/gates/{gate_id}/publish")

    async def rollback_gate(
        self,
        gate_id: str,
        *,
        version_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Rollback a gate to a previous version (async)."""
        body: Dict[str, Any] = {}
        if version_id is not None:
            body["versionId"] = version_id

        return await self._http.post(f"/api/flow/gates/{gate_id}/rollback", body)

    async def export_gate(self, gate_id: str) -> Dict[str, Any]:
        """Export a gate configuration (async)."""
        return await self._http.get(f"/api/flow/gates/{gate_id}/export")

    async def import_gate(self, *, data: Dict[str, Any]) -> Dict[str, Any]:
        """Import a gate from exported configuration (async)."""
        return await self._http.post("/api/flow/gates/import", data)

    async def test_gate(
        self,
        gate_id: str,
        *,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Test a gate with a payload (async, dry-run, no run created)."""
        return await self._http.post(
            f"/api/flow/gates/{gate_id}/test", {"payload": payload}
        )

    async def validate_gate(
        self,
        gate_id: str,
        *,
        payload: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        webhook_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Validate a payload against a gate (async, creates run with validation_id)."""
        body: Dict[str, Any] = {"payload": payload}
        if metadata is not None:
            body["metadata"] = metadata
        if webhook_url is not None:
            body["webhookUrl"] = webhook_url

        return await self._http.post(f"/api/flow/gates/{gate_id}/validate", body)

    async def verify_validation(
        self,
        *,
        validation_id: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Verify a validation result (async)."""
        return await self._http.post(
            "/api/flow/verify",
            {"validationId": validation_id, "payload": payload},
        )

    async def get_run_payload(
        self,
        run_id: str,
        *,
        field: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get the payload for a run (async)."""
        params: Dict[str, Any] = {}
        if field is not None:
            params["field"] = field

        return await self._http.get(f"/api/flow/runs/{run_id}/payload", params)

    async def get_run_chain(self, correlation_id: str) -> Dict[str, Any]:
        """Get a chain of runs by correlation ID (async)."""
        return await self._http.get(f"/api/flow/runs/chain/{correlation_id}")

    async def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Get a transaction by ID (async)."""
        return await self._http.get(f"/api/flow/transactions/{transaction_id}")

    async def list_gates(
        self,
        *,
        status: Optional[str] = None,
        limit: int = 20,
        page: int = 1,
    ) -> Dict[str, Any]:
        """List all gates (async)."""
        params: Dict[str, Any] = {"limit": limit, "page": page}
        if status:
            params["status"] = status

        response = await self._http.get("/api/flow/gates", params)
        return _paginate(response, "gates", page, limit)

    async def get_gate(self, gate_id: str) -> Dict[str, Any]:
        """Get a gate by ID (async)."""
        return await self._http.get(f"/api/flow/gates/{gate_id}")

    # ---- Runs ----

    async def submit_run(
        self,
        gate_id: str,
        *,
        input: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        webhook_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Submit a run to a gate for validation (async)."""
        body: Dict[str, Any] = {"payload": input}
        if metadata:
            body["metadata"] = metadata
        if webhook_url:
            body["webhookUrl"] = webhook_url

        response = await self._http.post(f"/api/flow/gates/{gate_id}/runs", body)
        # Map runId → id for consistency with get_run/list_runs
        if "runId" in response and "id" not in response:
            response["id"] = response["runId"]
        return response

    async def get_run(self, run_id: str) -> Dict[str, Any]:
        """Get a run by ID (async)."""
        return await self._http.get(f"/api/flow/runs/{run_id}")

    async def list_runs(
        self,
        *,
        status: Optional[str] = None,
        limit: int = 20,
        page: int = 1,
    ) -> Dict[str, Any]:
        """List all runs (async)."""
        params: Dict[str, Any] = {"limit": limit, "page": page}
        if status:
            params["status"] = status

        response = await self._http.get("/api/flow/runs", params)
        return _paginate(response, "runs", page, limit)

    async def list_runs_by_gate(
        self,
        gate_id: str,
        *,
        status: Optional[str] = None,
        limit: int = 20,
        page: int = 1,
    ) -> Dict[str, Any]:
        """List runs for a specific gate (async)."""
        params: Dict[str, Any] = {"limit": limit, "page": page}
        if status:
            params["status"] = status

        response = await self._http.get(f"/api/flow/gates/{gate_id}/runs", params)
        return _paginate(response, "runs", page, limit)

    async def list_active_runs(
        self,
        *,
        limit: int = 20,
        page: int = 1,
    ) -> Dict[str, Any]:
        """List active (non-terminal) runs (async)."""
        params: Dict[str, Any] = {"limit": limit, "page": page}

        response = await self._http.get("/api/flow/runs/active", params)
        return _paginate(response, "runs", page, limit)

    async def wait_for_run(
        self,
        run_id: str,
        *,
        poll_interval: float = 1.0,
        timeout: float = 60.0,
    ) -> Dict[str, Any]:
        """
        Wait for a run to reach a terminal state (async).

        Args:
            run_id: Run ID to wait for
            poll_interval: Time between polls in seconds (default: 1.0)
            timeout: Maximum wait time in seconds (default: 60.0)

        Returns:
            Completed run

        Raises:
            TimeoutError: If run doesn't complete within timeout
        """
        start_time = time.time()

        while True:
            run = await self.get_run(run_id)

            if run["status"] in TERMINAL_STATUSES:
                return run

            if time.time() - start_time > timeout:
                raise TimeoutError(f"Timeout waiting for run {run_id} to complete")

            await asyncio.sleep(poll_interval)

    # ---- Approvals ----

    async def list_approvals(
        self,
        *,
        status: Optional[str] = None,
        limit: int = 20,
        page: int = 1,
    ) -> Dict[str, Any]:
        """List approvals (async)."""
        params: Dict[str, Any] = {"limit": limit, "page": page}
        if status:
            params["status"] = status

        response = await self._http.get("/api/flow/approvals", params)
        return _paginate(response, "approvals", page, limit)

    async def approve(
        self,
        approval_id: str,
        *,
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Approve a pending approval (async)."""
        body: Dict[str, Any] = {}
        if note:
            body["note"] = note

        return await self._http.post(f"/api/flow/approvals/{approval_id}/approve", body)

    async def reject(
        self,
        approval_id: str,
        *,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Reject a pending approval (async)."""
        body: Dict[str, Any] = {}
        if reason:
            body["reason"] = reason

        return await self._http.post(f"/api/flow/approvals/{approval_id}/reject", body)

    async def resend_approval_email(self, run_id: str) -> Dict[str, Any]:
        """Resend approval notification emails for a run (async)."""
        return await self._http.post(f"/api/flow/approvals/resend/{run_id}", {})

    # ---- Deliveries ----

    async def list_deliveries(
        self,
        run_id: str,
        *,
        limit: int = 20,
        page: int = 1,
    ) -> Dict[str, Any]:
        """List deliveries for a run (async)."""
        params: Dict[str, Any] = {"limit": limit, "page": page}

        response = await self._http.get(f"/api/flow/runs/{run_id}/deliveries", params)
        return _paginate(response, "deliveries", page, limit)

    async def retry_delivery(self, delivery_id: str) -> Dict[str, Any]:
        """Retry a failed delivery (async)."""
        return await self._http.post(f"/api/flow/deliveries/{delivery_id}/retry", {})


def _paginate(
    response: Dict[str, Any], key: str, page: int, limit: int
) -> Dict[str, Any]:
    data = response.get("data", response.get(key, []))
    total = response.get("total", response.get("meta", {}).get("total", len(data)))

    return {
        "data": data,
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "totalPages": (total + limit - 1) // limit if limit > 0 else 1,
        },
    }
