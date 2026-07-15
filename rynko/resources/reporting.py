"""
Reporting Resource

Integrate an application (e.g. a WMS) with Rynko Reporting via an API key that
has an explicit report allow-list. All operations are scoped to that list.
"""

from typing import Any, Dict, List, Optional

from ..http import HttpClient, AsyncHttpClient


def _mint_body(
    report_ref: Optional[str],
    locked_params: Optional[Dict[str, Any]],
    actor: Optional[Dict[str, Any]],
    ttl_minutes: Optional[int],
) -> Dict[str, Any]:
    body: Dict[str, Any] = {}
    if report_ref is not None:
        body["reportRef"] = report_ref
    if locked_params is not None:
        body["lockedParams"] = locked_params
    if actor is not None:
        body["actor"] = actor
    if ttl_minutes is not None:
        body["ttlMinutes"] = ttl_minutes
    return body


def _run_body(
    report_ref: str,
    params: Optional[Dict[str, Any]],
    actor: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    body: Dict[str, Any] = {"reportRef": report_ref}
    if params is not None:
        body["params"] = params
    if actor is not None:
        body["actor"] = actor
    return body


class ReportingResource:
    """Synchronous Reporting resource."""

    def __init__(self, http: HttpClient):
        self._http = http

    def mint_run_link(
        self,
        *,
        report_ref: Optional[str] = None,
        locked_params: Optional[Dict[str, Any]] = None,
        actor: Optional[Dict[str, Any]] = None,
        ttl_minutes: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Mint a short-lived run link an operator can open (no Rynko login).

        Provide ``report_ref`` for a per-report link, or omit it for a landing
        link over the key's allow-list. ``locked_params`` are fixed by the caller
        and can't be changed by the operator. ``actor`` is the external user the
        run is attributed to (audit), e.g. ``{"externalUserId": "jdoe", "name": "Jane"}``.

        Returns:
            Dict with ``token``, ``url``, ``expiresAt``, ``mode``.

        Example:
            >>> link = client.reporting.mint_run_link(
            ...     report_ref="daily-progress",
            ...     locked_params={"warehouse": "W1"},
            ...     actor={"externalUserId": "jdoe", "name": "Jane Doe"},
            ...     ttl_minutes=15,
            ... )
            >>> # Redirect the operator's browser to link["url"]
        """
        return self._http.post(
            "/api/reporting/run-link/mint",
            _mint_body(report_ref, locked_params, actor, ttl_minutes),
        )

    def run_report(
        self,
        report_ref: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        actor: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run a report directly (server-to-server). The API key must have the
        report on its allow-list.

        Returns:
            Dict with ``runId`` and ``status``.
        """
        return self._http.post(
            "/api/reporting/run-link/run-direct", _run_body(report_ref, params, actor)
        )

    def list_reports(self) -> List[Dict[str, Any]]:
        """List the reports this API key is allowed to run (its allow-list)."""
        response = self._http.get("/api/reporting/run-link/reports")
        return response.get("reports", [])


class AsyncReportingResource:
    """Asynchronous Reporting resource."""

    def __init__(self, http: AsyncHttpClient):
        self._http = http

    async def mint_run_link(
        self,
        *,
        report_ref: Optional[str] = None,
        locked_params: Optional[Dict[str, Any]] = None,
        actor: Optional[Dict[str, Any]] = None,
        ttl_minutes: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Mint a short-lived run link (see :class:`ReportingResource`)."""
        return await self._http.post(
            "/api/reporting/run-link/mint",
            _mint_body(report_ref, locked_params, actor, ttl_minutes),
        )

    async def run_report(
        self,
        report_ref: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        actor: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run a report directly (see :class:`ReportingResource`)."""
        return await self._http.post(
            "/api/reporting/run-link/run-direct", _run_body(report_ref, params, actor)
        )

    async def list_reports(self) -> List[Dict[str, Any]]:
        """List the reports this API key is allowed to run."""
        response = await self._http.get("/api/reporting/run-link/reports")
        return response.get("reports", [])
