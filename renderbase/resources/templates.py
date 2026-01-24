"""
Templates Resource
"""

from typing import Any, Dict, Optional

from ..http import HttpClient, AsyncHttpClient


class TemplatesResource:
    """Synchronous templates resource."""

    def __init__(self, http: HttpClient):
        self._http = http

    def get(self, template_id: str) -> Dict[str, Any]:
        """
        Get a template by ID.

        Example:
            >>> template = client.templates.get("tmpl_abc123")
            >>> print(f"Template: {template['name']}")
            >>> print(f"Variables: {template['variables']}")
        """
        # Backend returns template directly
        return self._http.get(f"/api/templates/{template_id}")

    def list(
        self,
        *,
        limit: int = 20,
        page: int = 1,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List templates with optional filters.

        Args:
            limit: Results per page
            page: Page number
            search: Search by template name

        Returns:
            Dict with 'data' and pagination info

        Example:
            >>> result = client.templates.list()
            >>> print(f"Found {len(result['data'])} templates")
        """
        params = {
            "limit": limit,
            "page": page,
            "search": search,
        }
        return self._http.get("/api/templates/attachment", params)

    def list_pdf(self, *, limit: int = 20, page: int = 1) -> Dict[str, Any]:
        """List PDF templates (client-side filter by outputFormats)."""
        result = self.list(limit=limit, page=page)
        if "data" in result:
            result["data"] = [
                t for t in result["data"]
                if "pdf" in (t.get("outputFormats") or [])
            ]
        return result

    def list_excel(self, *, limit: int = 20, page: int = 1) -> Dict[str, Any]:
        """List Excel templates (client-side filter by outputFormats)."""
        result = self.list(limit=limit, page=page)
        if "data" in result:
            result["data"] = [
                t for t in result["data"]
                if "xlsx" in (t.get("outputFormats") or []) or "excel" in (t.get("outputFormats") or [])
            ]
        return result


class AsyncTemplatesResource:
    """Asynchronous templates resource."""

    def __init__(self, http: AsyncHttpClient):
        self._http = http

    async def get(self, template_id: str) -> Dict[str, Any]:
        """
        Get a template by ID (async).

        Example:
            >>> template = await client.templates.get("tmpl_abc123")
            >>> print(f"Template: {template['name']}")
        """
        # Backend returns template directly
        return await self._http.get(f"/api/templates/{template_id}")

    async def list(
        self,
        *,
        limit: int = 20,
        page: int = 1,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List templates (async)."""
        params = {
            "limit": limit,
            "page": page,
            "search": search,
        }
        return await self._http.get("/api/templates/attachment", params)

    async def list_pdf(self, *, limit: int = 20, page: int = 1) -> Dict[str, Any]:
        """List PDF templates (async, client-side filter by outputFormats)."""
        result = await self.list(limit=limit, page=page)
        if "data" in result:
            result["data"] = [
                t for t in result["data"]
                if "pdf" in (t.get("outputFormats") or [])
            ]
        return result

    async def list_excel(self, *, limit: int = 20, page: int = 1) -> Dict[str, Any]:
        """List Excel templates (async, client-side filter by outputFormats)."""
        result = await self.list(limit=limit, page=page)
        if "data" in result:
            result["data"] = [
                t for t in result["data"]
                if "xlsx" in (t.get("outputFormats") or []) or "excel" in (t.get("outputFormats") or [])
            ]
        return result
