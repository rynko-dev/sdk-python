"""
Flow Resource
"""

import asyncio
import time
from typing import Any, Dict, List, Optional


from ..http import HttpClient, AsyncHttpClient

TERMINAL_STATUSES = frozenset({
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

    # ---- Gates (read-only) ----

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

        return self._http.post(f"/api/flow/gates/{gate_id}/runs", body)

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

    # ---- Gates (read-only) ----

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

        return await self._http.post(f"/api/flow/gates/{gate_id}/runs", body)

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
