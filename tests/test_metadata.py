#!/usr/bin/env python3
"""
Metadata Unit Tests

Tests for metadata type definitions and webhook event parsing.
These tests don't require a live API.
"""

import hashlib
import hmac
import json
import time
import unittest

from rynko import verify_webhook_signature, WebhookSignatureError


class TestMetadataTypes(unittest.TestCase):
    """Tests for metadata value types."""

    def test_metadata_string_values(self):
        """Metadata should accept string values."""
        metadata = {"orderId": "ord_12345", "customerId": "cust_67890"}
        self.assertEqual(metadata["orderId"], "ord_12345")
        self.assertEqual(metadata["customerId"], "cust_67890")

    def test_metadata_number_values(self):
        """Metadata should accept number values."""
        metadata = {"priority": 1, "amount": 99.99}
        self.assertEqual(metadata["priority"], 1)
        self.assertEqual(metadata["amount"], 99.99)

    def test_metadata_boolean_values(self):
        """Metadata should accept boolean values."""
        metadata = {"isUrgent": True, "isTest": False}
        self.assertTrue(metadata["isUrgent"])
        self.assertFalse(metadata["isTest"])

    def test_metadata_null_values(self):
        """Metadata should accept null values."""
        metadata = {"discount": None}
        self.assertIsNone(metadata["discount"])

    def test_metadata_mixed_values(self):
        """Metadata should accept mixed value types."""
        metadata = {
            "orderId": "ord_12345",
            "priority": 1,
            "amount": 99.99,
            "isUrgent": True,
            "discount": None,
        }
        self.assertEqual(metadata["orderId"], "ord_12345")
        self.assertEqual(metadata["priority"], 1)
        self.assertEqual(metadata["amount"], 99.99)
        self.assertTrue(metadata["isUrgent"])
        self.assertIsNone(metadata["discount"])


class TestWebhookEventParsing(unittest.TestCase):
    """Tests for webhook event parsing with metadata."""

    TEST_SECRET = "whsec_test_secret"

    def _create_signature(self, payload: str, timestamp: int) -> str:
        """Create a valid webhook signature."""
        signed_payload = f"{timestamp}.{payload}"
        signature = hmac.new(
            self.TEST_SECRET.encode("utf-8"),
            signed_payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return f"t={timestamp},v1={signature}"

    def test_document_completed_with_metadata(self):
        """Should parse document.generated event with metadata."""
        timestamp = int(time.time())
        payload = json.dumps({
            "id": "evt_123",
            "type": "document.generated",
            "timestamp": "2025-02-02T12:00:00Z",
            "data": {
                "jobId": "job_456",
                "status": "completed",
                "templateId": "tmpl_789",
                "format": "pdf",
                "downloadUrl": "https://example.com/download",
                "fileSize": 12345,
                "metadata": {
                    "orderId": "ord_abc",
                    "customerId": "cust_def",
                    "priority": 1,
                },
            },
        })

        signature = self._create_signature(payload, timestamp)
        event = verify_webhook_signature(
            payload=payload,
            signature=signature,
            secret=self.TEST_SECRET,
        )

        self.assertEqual(event["id"], "evt_123")
        self.assertEqual(event["type"], "document.generated")

        data = event["data"]
        self.assertEqual(data["jobId"], "job_456")
        self.assertEqual(data["status"], "completed")
        self.assertEqual(data["downloadUrl"], "https://example.com/download")
        self.assertIsNotNone(data.get("metadata"))
        self.assertEqual(data["metadata"]["orderId"], "ord_abc")
        self.assertEqual(data["metadata"]["customerId"], "cust_def")
        self.assertEqual(data["metadata"]["priority"], 1)

    def test_document_failed_with_metadata(self):
        """Should parse document.failed event with error and metadata."""
        timestamp = int(time.time())
        payload = json.dumps({
            "id": "evt_fail",
            "type": "document.failed",
            "timestamp": "2025-02-02T12:00:00Z",
            "data": {
                "jobId": "job_fail",
                "status": "failed",
                "templateId": "tmpl_789",
                "format": "pdf",
                "errorMessage": "Template not found",
                "errorCode": "ERR_TMPL_001",
                "metadata": {
                    "orderId": "ord_failed",
                },
            },
        })

        signature = self._create_signature(payload, timestamp)
        event = verify_webhook_signature(
            payload=payload,
            signature=signature,
            secret=self.TEST_SECRET,
        )

        self.assertEqual(event["type"], "document.failed")

        data = event["data"]
        self.assertEqual(data["status"], "failed")
        self.assertEqual(data["errorMessage"], "Template not found")
        self.assertEqual(data["errorCode"], "ERR_TMPL_001")
        self.assertNotIn("downloadUrl", data)
        self.assertEqual(data["metadata"]["orderId"], "ord_failed")

    def test_document_event_without_metadata(self):
        """Should parse event without metadata."""
        timestamp = int(time.time())
        payload = json.dumps({
            "id": "evt_no_meta",
            "type": "document.generated",
            "timestamp": "2025-02-02T12:00:00Z",
            "data": {
                "jobId": "job_789",
                "status": "completed",
                "templateId": "tmpl_abc",
                "format": "pdf",
                "downloadUrl": "https://example.com/dl",
            },
        })

        signature = self._create_signature(payload, timestamp)
        event = verify_webhook_signature(
            payload=payload,
            signature=signature,
            secret=self.TEST_SECRET,
        )

        data = event["data"]
        self.assertEqual(data["jobId"], "job_789")
        self.assertIsNone(data.get("metadata"))

    def test_batch_completed_with_metadata(self):
        """Should parse batch.completed event with metadata."""
        timestamp = int(time.time())
        payload = json.dumps({
            "id": "evt_batch",
            "type": "batch.completed",
            "timestamp": "2025-02-02T12:00:00Z",
            "data": {
                "batchId": "batch_123",
                "status": "completed",
                "templateId": "tmpl_456",
                "format": "pdf",
                "totalJobs": 10,
                "completedJobs": 8,
                "failedJobs": 2,
                "metadata": {
                    "batchRunId": "run_001",
                    "triggeredBy": "scheduled_job",
                },
            },
        })

        signature = self._create_signature(payload, timestamp)
        event = verify_webhook_signature(
            payload=payload,
            signature=signature,
            secret=self.TEST_SECRET,
        )

        self.assertEqual(event["type"], "batch.completed")

        data = event["data"]
        self.assertEqual(data["batchId"], "batch_123")
        self.assertEqual(data["totalJobs"], 10)
        self.assertEqual(data["completedJobs"], 8)
        self.assertEqual(data["failedJobs"], 2)
        self.assertEqual(data["metadata"]["batchRunId"], "run_001")
        self.assertEqual(data["metadata"]["triggeredBy"], "scheduled_job")


if __name__ == "__main__":
    unittest.main()
