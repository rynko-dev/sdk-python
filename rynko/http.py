"""
HTTP Client for Rynko SDK with automatic retry and exponential backoff
"""

import random
import time
import asyncio
from typing import Any, Dict, Optional, Set
from dataclasses import dataclass, field

import httpx

from .exceptions import RynkoError


@dataclass
class RetryConfig:
    """Configuration for automatic retry with exponential backoff."""

    # Maximum number of retry attempts (default: 5)
    max_attempts: int = 5

    # Initial delay between retries in seconds (default: 1.0)
    initial_delay: float = 1.0

    # Maximum delay between retries in seconds (default: 30.0)
    max_delay: float = 30.0

    # Maximum jitter to add to delay in seconds (default: 1.0)
    max_jitter: float = 1.0

    # HTTP status codes that should trigger a retry (default: 429, 503, 504)
    retryable_statuses: Set[int] = field(default_factory=lambda: {429, 503, 504})


# Default retry configuration
DEFAULT_RETRY_CONFIG = RetryConfig()


def _calculate_delay(
    attempt: int,
    config: RetryConfig,
    retry_after: Optional[float] = None,
) -> float:
    """Calculate delay for exponential backoff with jitter."""
    # If server specified Retry-After, respect it (with jitter)
    if retry_after is not None:
        jitter = random.random() * config.max_jitter
        return min(retry_after + jitter, config.max_delay)

    # Exponential backoff: initial_delay * 2^attempt
    exponential_delay = config.initial_delay * (2 ** attempt)

    # Add random jitter to prevent thundering herd
    jitter = random.random() * config.max_jitter

    # Cap at max_delay
    return min(exponential_delay + jitter, config.max_delay)


def _parse_retry_after(retry_after: Optional[str]) -> Optional[float]:
    """Parse Retry-After header value to seconds."""
    if not retry_after:
        return None

    # Try to parse as integer (seconds)
    try:
        return float(retry_after)
    except ValueError:
        pass

    # Try to parse as HTTP-date (not commonly used but supported)
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(retry_after)
        delay = (dt.timestamp() - time.time())
        return delay if delay > 0 else None
    except Exception:
        pass

    return None


class HttpClient:
    """Synchronous HTTP client with automatic retry."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
        retry: Optional[RetryConfig] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "rynko-python/1.0.0",
            **(headers or {}),
        }
        self._client = httpx.Client(timeout=timeout)
        self._retry_config = retry if retry is not None else DEFAULT_RETRY_CONFIG

    def _should_retry(self, status_code: int) -> bool:
        """Check if the status code should trigger a retry."""
        if self._retry_config is None:
            return False
        return status_code in self._retry_config.retryable_statuses

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle API response and errors."""
        try:
            data = response.json()
        except Exception:
            data = {}

        if response.status_code >= 400:
            message = data.get("message", f"HTTP {response.status_code}")
            code = data.get("error", "ApiError")
            raise RynkoError(message, code, response.status_code)

        return data

    def _request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a request with automatic retry on retryable errors."""
        max_attempts = self._retry_config.max_attempts if self._retry_config else 1
        last_error: Optional[RynkoError] = None

        # Allow callers to override headers (e.g., for multipart requests)
        request_headers = kwargs.pop("headers", self._headers)

        for attempt in range(max_attempts):
            try:
                response = self._client.request(
                    method,
                    url,
                    headers=request_headers,
                    **kwargs,
                )

                # Check if we should retry
                if self._should_retry(response.status_code):
                    retry_after = _parse_retry_after(
                        response.headers.get("Retry-After")
                    )
                    delay = _calculate_delay(attempt, self._retry_config, retry_after)

                    # Store the error in case this is the last attempt
                    try:
                        data = response.json()
                    except Exception:
                        data = {}
                    last_error = RynkoError(
                        data.get("message", f"HTTP {response.status_code}"),
                        data.get("error", "ApiError"),
                        response.status_code,
                    )

                    # If we have more attempts, wait and retry
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                        continue

                return self._handle_response(response)

            except RynkoError as e:
                # If it's a retryable error and we have attempts left
                if self._should_retry(e.status_code) and attempt < max_attempts - 1:
                    last_error = e
                    delay = _calculate_delay(attempt, self._retry_config)
                    time.sleep(delay)
                    continue
                raise

        # If we've exhausted all retries, throw the last error
        if last_error:
            raise last_error

        raise RynkoError("Request failed after retries", "RetryExhausted", 0)

    def get(
        self, path: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make GET request."""
        # Filter out None values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        return self._request_with_retry(
            "GET",
            f"{self.base_url}{path}",
            params=params,
        )

    def post(
        self, path: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make POST request."""
        return self._request_with_retry(
            "POST",
            f"{self.base_url}{path}",
            json=data,
        )

    def put(
        self, path: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make PUT request."""
        return self._request_with_retry(
            "PUT",
            f"{self.base_url}{path}",
            json=data,
        )

    def patch(
        self, path: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make PATCH request."""
        return self._request_with_retry(
            "PATCH",
            f"{self.base_url}{path}",
            json=data,
        )

    def delete(self, path: str) -> Dict[str, Any]:
        """Make DELETE request."""
        return self._request_with_retry(
            "DELETE",
            f"{self.base_url}{path}",
        )

    def post_multipart(
        self,
        path: str,
        *,
        files: Any,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make multipart POST request with file uploads."""
        # For multipart requests, remove Content-Type so httpx sets it with boundary
        headers = {k: v for k, v in self._headers.items() if k != "Content-Type"}
        return self._request_with_retry(
            "POST",
            f"{self.base_url}{path}",
            files=files,
            data=data,
            headers=headers,
        )

    def get_raw(self, url: str) -> bytes:
        """Make a GET request and return raw bytes (for downloading files)."""
        response = self._client.request(
            "GET",
            url,
            headers=self._headers,
        )
        if response.status_code >= 400:
            raise RynkoError(
                f"HTTP {response.status_code}",
                "DownloadError",
                response.status_code,
            )
        return response.content

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()


class AsyncHttpClient:
    """Asynchronous HTTP client with automatic retry."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
        retry: Optional[RetryConfig] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "rynko-python/1.0.0",
            **(headers or {}),
        }
        self._client = httpx.AsyncClient(timeout=timeout)
        self._retry_config = retry if retry is not None else DEFAULT_RETRY_CONFIG

    def _should_retry(self, status_code: int) -> bool:
        """Check if the status code should trigger a retry."""
        if self._retry_config is None:
            return False
        return status_code in self._retry_config.retryable_statuses

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle API response and errors."""
        try:
            data = response.json()
        except Exception:
            data = {}

        if response.status_code >= 400:
            message = data.get("message", f"HTTP {response.status_code}")
            code = data.get("error", "ApiError")
            raise RynkoError(message, code, response.status_code)

        return data

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a request with automatic retry on retryable errors."""
        max_attempts = self._retry_config.max_attempts if self._retry_config else 1
        last_error: Optional[RynkoError] = None

        # Allow callers to override headers (e.g., for multipart requests)
        request_headers = kwargs.pop("headers", self._headers)

        for attempt in range(max_attempts):
            try:
                response = await self._client.request(
                    method,
                    url,
                    headers=request_headers,
                    **kwargs,
                )

                # Check if we should retry
                if self._should_retry(response.status_code):
                    retry_after = _parse_retry_after(
                        response.headers.get("Retry-After")
                    )
                    delay = _calculate_delay(attempt, self._retry_config, retry_after)

                    # Store the error in case this is the last attempt
                    try:
                        data = response.json()
                    except Exception:
                        data = {}
                    last_error = RynkoError(
                        data.get("message", f"HTTP {response.status_code}"),
                        data.get("error", "ApiError"),
                        response.status_code,
                    )

                    # If we have more attempts, wait and retry
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay)
                        continue

                return self._handle_response(response)

            except RynkoError as e:
                # If it's a retryable error and we have attempts left
                if self._should_retry(e.status_code) and attempt < max_attempts - 1:
                    last_error = e
                    delay = _calculate_delay(attempt, self._retry_config)
                    await asyncio.sleep(delay)
                    continue
                raise

        # If we've exhausted all retries, throw the last error
        if last_error:
            raise last_error

        raise RynkoError("Request failed after retries", "RetryExhausted", 0)

    async def get(
        self, path: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make GET request."""
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        return await self._request_with_retry(
            "GET",
            f"{self.base_url}{path}",
            params=params,
        )

    async def post(
        self, path: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make POST request."""
        return await self._request_with_retry(
            "POST",
            f"{self.base_url}{path}",
            json=data,
        )

    async def put(
        self, path: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make PUT request."""
        return await self._request_with_retry(
            "PUT",
            f"{self.base_url}{path}",
            json=data,
        )

    async def patch(
        self, path: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make PATCH request."""
        return await self._request_with_retry(
            "PATCH",
            f"{self.base_url}{path}",
            json=data,
        )

    async def delete(self, path: str) -> Dict[str, Any]:
        """Make DELETE request."""
        return await self._request_with_retry(
            "DELETE",
            f"{self.base_url}{path}",
        )

    async def post_multipart(
        self,
        path: str,
        *,
        files: Any,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make multipart POST request with file uploads (async)."""
        # For multipart requests, remove Content-Type so httpx sets it with boundary
        headers = {k: v for k, v in self._headers.items() if k != "Content-Type"}
        return await self._request_with_retry(
            "POST",
            f"{self.base_url}{path}",
            files=files,
            data=data,
            headers=headers,
        )

    async def get_raw(self, url: str) -> bytes:
        """Make a GET request and return raw bytes (async, for downloading files)."""
        response = await self._client.request(
            "GET",
            url,
            headers=self._headers,
        )
        if response.status_code >= 400:
            raise RynkoError(
                f"HTTP {response.status_code}",
                "DownloadError",
                response.status_code,
            )
        return response.content

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
