"""
Webhooks Resource

Provides access to webhook subscriptions including CRUD operations,
secret rotation, testing, and delivery management.
"""

from typing import Any, Dict, List, Optional

from ..http import HttpClient, AsyncHttpClient


class WebhooksResource:
    """Synchronous webhooks resource."""

    def __init__(self, http: HttpClient):
        self._http = http

    def get(self, webhook_id: str) -> Dict[str, Any]:
        """Get a webhook subscription by ID."""
        response = self._http.get(f"/api/v1/webhook-subscriptions/{webhook_id}")
        return response.get("data", response)

    def list(self) -> Dict[str, Any]:
        """List all webhook subscriptions."""
        return self._http.get("/api/v1/webhook-subscriptions")

    def create(
        self,
        *,
        url: str,
        events: List[str],
        description: Optional[str] = None,
        is_active: bool = True,
        max_retries: Optional[int] = None,
        timeout_ms: Optional[int] = None,
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a webhook subscription.

        Args:
            url: The URL to deliver webhook events to
            events: List of event types to subscribe to
            description: Optional description for the webhook
            is_active: Whether the webhook is active (default: True)
            max_retries: Maximum number of delivery retries
            timeout_ms: Delivery timeout in milliseconds
            workspace_id: Optional workspace ID to scope the webhook

        Returns:
            Created webhook subscription

        Example:
            >>> webhook = client.webhooks.create(
            ...     url="https://your-app.com/webhooks/rynko",
            ...     events=["document.generated", "document.failed"],
            ...     description="Production document notifications",
            ... )
            >>> print(f"Webhook ID: {webhook['id']}")
            >>> print(f"Secret: {webhook['secret']}")
        """
        body: Dict[str, Any] = {
            "url": url,
            "events": events,
            "isActive": is_active,
        }
        if description is not None:
            body["description"] = description
        if max_retries is not None:
            body["maxRetries"] = max_retries
        if timeout_ms is not None:
            body["timeoutMs"] = timeout_ms
        if workspace_id is not None:
            body["workspaceId"] = workspace_id

        response = self._http.post("/api/v1/webhook-subscriptions", body)
        return response.get("data", response)

    def update(
        self,
        webhook_id: str,
        *,
        description: Optional[str] = None,
        events: Optional[List[str]] = None,
        is_active: Optional[bool] = None,
        max_retries: Optional[int] = None,
        timeout_ms: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Update a webhook subscription.

        Args:
            webhook_id: Webhook subscription ID
            description: Updated description
            events: Updated list of event types
            is_active: Updated active status
            max_retries: Updated maximum retries
            timeout_ms: Updated timeout in milliseconds

        Returns:
            Updated webhook subscription

        Example:
            >>> webhook = client.webhooks.update(
            ...     "wh_abc123",
            ...     events=["document.generated"],
            ...     is_active=False,
            ... )
        """
        body: Dict[str, Any] = {}
        if description is not None:
            body["description"] = description
        if events is not None:
            body["events"] = events
        if is_active is not None:
            body["isActive"] = is_active
        if max_retries is not None:
            body["maxRetries"] = max_retries
        if timeout_ms is not None:
            body["timeoutMs"] = timeout_ms

        response = self._http.patch(f"/api/v1/webhook-subscriptions/{webhook_id}", body)
        return response.get("data", response)

    def delete(self, webhook_id: str) -> Dict[str, Any]:
        """
        Delete a webhook subscription.

        Args:
            webhook_id: Webhook subscription ID

        Returns:
            Deletion confirmation

        Example:
            >>> client.webhooks.delete("wh_abc123")
        """
        response = self._http.delete(f"/api/v1/webhook-subscriptions/{webhook_id}")
        return response.get("data", response)

    def rotate_secret(self, webhook_id: str) -> Dict[str, Any]:
        """
        Rotate the signing secret for a webhook subscription.

        Args:
            webhook_id: Webhook subscription ID

        Returns:
            Updated webhook with new secret

        Example:
            >>> result = client.webhooks.rotate_secret("wh_abc123")
            >>> print(f"New secret: {result['secret']}")
        """
        response = self._http.post(
            f"/api/v1/webhook-subscriptions/{webhook_id}/rotate-secret"
        )
        return response.get("data", response)

    def test(self, webhook_id: str) -> Dict[str, Any]:
        """
        Send a test event to a webhook subscription.

        Args:
            webhook_id: Webhook subscription ID

        Returns:
            Test delivery result

        Example:
            >>> result = client.webhooks.test("wh_abc123")
            >>> print(f"Delivery status: {result['status']}")
        """
        response = self._http.post(
            f"/api/v1/webhook-subscriptions/{webhook_id}/test"
        )
        return response.get("data", response)

    def list_deliveries(
        self,
        webhook_id: str,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List deliveries for a webhook subscription.

        Args:
            webhook_id: Webhook subscription ID
            limit: Maximum number of deliveries to return
            offset: Number of deliveries to skip

        Returns:
            Dict with delivery list and pagination info

        Example:
            >>> result = client.webhooks.list_deliveries("wh_abc123")
            >>> for delivery in result.get("data", []):
            ...     print(f"{delivery['id']}: {delivery['status']}")
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset

        return self._http.get(
            f"/api/v1/webhook-subscriptions/{webhook_id}/deliveries", params
        )

    def retry_delivery(self, webhook_id: str, delivery_id: str) -> Dict[str, Any]:
        """
        Retry a failed webhook delivery.

        Args:
            webhook_id: Webhook subscription ID
            delivery_id: Delivery ID to retry

        Returns:
            Retry result

        Example:
            >>> result = client.webhooks.retry_delivery("wh_abc123", "del_xyz789")
        """
        response = self._http.post(
            f"/api/v1/webhook-subscriptions/{webhook_id}/deliveries/{delivery_id}/retry"
        )
        return response.get("data", response)


class AsyncWebhooksResource:
    """Asynchronous webhooks resource."""

    def __init__(self, http: AsyncHttpClient):
        self._http = http

    async def get(self, webhook_id: str) -> Dict[str, Any]:
        """Get a webhook subscription by ID (async)."""
        response = await self._http.get(f"/api/v1/webhook-subscriptions/{webhook_id}")
        return response.get("data", response)

    async def list(self) -> Dict[str, Any]:
        """List all webhook subscriptions (async)."""
        return await self._http.get("/api/v1/webhook-subscriptions")

    async def create(
        self,
        *,
        url: str,
        events: List[str],
        description: Optional[str] = None,
        is_active: bool = True,
        max_retries: Optional[int] = None,
        timeout_ms: Optional[int] = None,
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a webhook subscription (async)."""
        body: Dict[str, Any] = {
            "url": url,
            "events": events,
            "isActive": is_active,
        }
        if description is not None:
            body["description"] = description
        if max_retries is not None:
            body["maxRetries"] = max_retries
        if timeout_ms is not None:
            body["timeoutMs"] = timeout_ms
        if workspace_id is not None:
            body["workspaceId"] = workspace_id

        response = await self._http.post("/api/v1/webhook-subscriptions", body)
        return response.get("data", response)

    async def update(
        self,
        webhook_id: str,
        *,
        description: Optional[str] = None,
        events: Optional[List[str]] = None,
        is_active: Optional[bool] = None,
        max_retries: Optional[int] = None,
        timeout_ms: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Update a webhook subscription (async)."""
        body: Dict[str, Any] = {}
        if description is not None:
            body["description"] = description
        if events is not None:
            body["events"] = events
        if is_active is not None:
            body["isActive"] = is_active
        if max_retries is not None:
            body["maxRetries"] = max_retries
        if timeout_ms is not None:
            body["timeoutMs"] = timeout_ms

        response = await self._http.patch(
            f"/api/v1/webhook-subscriptions/{webhook_id}", body
        )
        return response.get("data", response)

    async def delete(self, webhook_id: str) -> Dict[str, Any]:
        """Delete a webhook subscription (async)."""
        response = await self._http.delete(
            f"/api/v1/webhook-subscriptions/{webhook_id}"
        )
        return response.get("data", response)

    async def rotate_secret(self, webhook_id: str) -> Dict[str, Any]:
        """Rotate the signing secret for a webhook subscription (async)."""
        response = await self._http.post(
            f"/api/v1/webhook-subscriptions/{webhook_id}/rotate-secret"
        )
        return response.get("data", response)

    async def test(self, webhook_id: str) -> Dict[str, Any]:
        """Send a test event to a webhook subscription (async)."""
        response = await self._http.post(
            f"/api/v1/webhook-subscriptions/{webhook_id}/test"
        )
        return response.get("data", response)

    async def list_deliveries(
        self,
        webhook_id: str,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List deliveries for a webhook subscription (async)."""
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset

        return await self._http.get(
            f"/api/v1/webhook-subscriptions/{webhook_id}/deliveries", params
        )

    async def retry_delivery(self, webhook_id: str, delivery_id: str) -> Dict[str, Any]:
        """Retry a failed webhook delivery (async)."""
        response = await self._http.post(
            f"/api/v1/webhook-subscriptions/{webhook_id}/deliveries/{delivery_id}/retry"
        )
        return response.get("data", response)
