#!/usr/bin/env python3
"""
Batch Document Generation Example

This example shows how to generate multiple documents in a single request,
with both batch-level and per-document metadata for tracking.

Usage:
    RYNKO_API_KEY=your_key python examples/batch_generate.py
"""

import os
from rynko import Rynko


def main():
    client = Rynko(api_key=os.environ["RYNKO_API_KEY"])

    # Get first available template
    result = client.templates.list(limit=1)
    templates = result["data"]
    if not templates:
        print("No templates found. Create a template first.")
        return

    template = templates[0]
    print(f"Using template: {template['name']}")

    # Generate multiple documents with metadata
    batch = client.documents.generate_batch(
        template_id=template["id"],
        format="pdf",
        # Batch-level metadata (applies to the entire batch)
        metadata={
            "batchRunId": "run_20250202",
            "triggeredBy": "scheduled_job",
        },
        # Each document can have its own variables and metadata
        documents=[
            {
                "variables": {"invoiceNumber": "INV-001", "customerName": "Alice", "total": 150.0},
                "metadata": {"orderId": "ord_001", "customerId": "cust_alice"},
            },
            {
                "variables": {"invoiceNumber": "INV-002", "customerName": "Bob", "total": 275.5},
                "metadata": {"orderId": "ord_002", "customerId": "cust_bob"},
            },
            {
                "variables": {"invoiceNumber": "INV-003", "customerName": "Charlie", "total": 89.99},
                "metadata": {"orderId": "ord_003", "customerId": "cust_charlie"},
            },
        ],
    )

    print(f"Batch queued: {batch['batchId']}")
    print(f"Total jobs: {batch['totalJobs']}")
    print(f"Status: {batch['status']}")
    print(f"Estimated wait: {batch['estimatedWaitSeconds']} seconds")
    print()
    print("Metadata will be returned in webhook payloads:")
    print("  - Batch-level metadata in batch.completed event")
    print("  - Per-document metadata in each document.generated/failed event")
    print()
    print("Use metadata to correlate webhook events with your orders.")


if __name__ == "__main__":
    main()
