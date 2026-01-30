#!/usr/bin/env python3
"""
Batch Document Generation Example

This example shows how to generate multiple documents in a single request.

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

    # Generate multiple documents
    batch = client.documents.generate_batch(
        template_id=template["id"],
        format="pdf",
        documents=[
            {"invoiceNumber": "INV-001", "customerName": "Alice", "total": 150.0},
            {"invoiceNumber": "INV-002", "customerName": "Bob", "total": 275.5},
            {"invoiceNumber": "INV-003", "customerName": "Charlie", "total": 89.99},
        ],
    )

    print(f"Batch queued: {batch['batchId']}")
    print(f"Total jobs: {batch['totalJobs']}")
    print(f"Status: {batch['status']}")
    print(f"Estimated wait: {batch['estimatedWaitSeconds']} seconds")

    # Note: Use webhooks to get notified when batch completes
    # Or poll the individual job statuses


if __name__ == "__main__":
    main()
