"""
Rynko SDK Client
"""

from typing import Any, Dict, Optional, Union

from .http import HttpClient, AsyncHttpClient, RetryConfig
from .resources.documents import DocumentsResource, AsyncDocumentsResource
from .resources.extract import ExtractResource, AsyncExtractResource
from .resources.flow import FlowResource, AsyncFlowResource
from .resources.templates import TemplatesResource, AsyncTemplatesResource
from .resources.webhooks import WebhooksResource, AsyncWebhooksResource


DEFAULT_BASE_URL = "https://api.rynko.dev"
DEFAULT_TIMEOUT = 30.0


class Rynko:
    """
    Synchronous Rynko client.

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

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        headers: Optional[Dict[str, str]] = None,
        retry: Optional[Union[RetryConfig, bool]] = None,
    ):
        """
        Create a new Rynko client.

        Args:
            api_key: Your Rynko API key
            base_url: API base URL (default: https://api.rynko.dev)
            timeout: Request timeout in seconds (default: 30)
            headers: Additional headers to include in requests
            retry: Retry configuration. Pass RetryConfig for custom settings,
                   True/None for defaults, or False to disable retries.
        """
        if not api_key:
            raise ValueError("api_key is required")

        # Handle retry configuration
        retry_config: Optional[RetryConfig] = None
        if retry is False:
            retry_config = None
        elif retry is True or retry is None:
            retry_config = RetryConfig()
        else:
            retry_config = retry

        self._http = HttpClient(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            headers=headers,
            retry=retry_config,
        )

        self.documents = DocumentsResource(self._http)
        self.extract = ExtractResource(self._http)
        self.flow = FlowResource(self._http)
        self.templates = TemplatesResource(self._http)
        self.webhooks = WebhooksResource(self._http)

    def me(self) -> Dict[str, Any]:
        """Get the current authenticated user."""
        response = self._http.get("/api/auth/verify")
        return response.get("data", response)

    def verify_api_key(self) -> bool:
        """Verify the API key is valid."""
        try:
            self.me()
            return True
        except Exception:
            return False

    def close(self) -> None:
        """Close the HTTP client."""
        self._http.close()

    def __enter__(self) -> "Rynko":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncRynko:
    """
    Asynchronous Rynko client.

    Example:
        >>> from rynko import AsyncRynko
        >>> import asyncio
        >>>
        >>> async def main():
        ...     async with AsyncRynko(api_key="your_api_key") as client:
        ...         result = await client.documents.generate(
        ...             template_id="tmpl_invoice",
        ...             format="pdf",
        ...             variables={"invoiceNumber": "INV-001"}
        ...         )
        ...         print(f"Job ID: {result['jobId']}")
        ...         print(f"Download URL: {result['downloadUrl']}")
        >>>
        >>> asyncio.run(main())
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        headers: Optional[Dict[str, str]] = None,
        retry: Optional[Union[RetryConfig, bool]] = None,
    ):
        """
        Create a new async Rynko client.

        Args:
            api_key: Your Rynko API key
            base_url: API base URL (default: https://api.rynko.dev)
            timeout: Request timeout in seconds (default: 30)
            headers: Additional headers to include in requests
            retry: Retry configuration. Pass RetryConfig for custom settings,
                   True/None for defaults, or False to disable retries.
        """
        if not api_key:
            raise ValueError("api_key is required")

        # Handle retry configuration
        retry_config: Optional[RetryConfig] = None
        if retry is False:
            retry_config = None
        elif retry is True or retry is None:
            retry_config = RetryConfig()
        else:
            retry_config = retry

        self._http = AsyncHttpClient(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            headers=headers,
            retry=retry_config,
        )

        self.documents = AsyncDocumentsResource(self._http)
        self.extract = AsyncExtractResource(self._http)
        self.flow = AsyncFlowResource(self._http)
        self.templates = AsyncTemplatesResource(self._http)
        self.webhooks = AsyncWebhooksResource(self._http)

    async def me(self) -> Dict[str, Any]:
        """Get the current authenticated user (async)."""
        response = await self._http.get("/api/auth/verify")
        return response.get("data", response)

    async def verify_api_key(self) -> bool:
        """Verify the API key is valid (async)."""
        try:
            await self.me()
            return True
        except Exception:
            return False

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._http.close()

    async def __aenter__(self) -> "AsyncRynko":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
