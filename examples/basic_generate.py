#!/usr/bin/env python3
"""
Basic Document Generation Example

This example shows how to generate a PDF document and wait for completion.

Usage:
    RYNKO_API_KEY=your_key python examples/basic_generate.py
"""

import os
from rynko import Rynko


def main():
    client = Rynko(api_key=os.environ["RYNKO_API_KEY"])

    # Verify authentication
    user = client.me()
    print(f"Authenticated as: {user['email']}")

    # Get first available template
    result = client.templates.list(limit=1)
    templates = result["data"]
    if not templates:
        print("No templates found. Create a template first.")
        return

    template = templates[0]
    print(f"Using template: {template['name']} ({template['id']})")

    # Queue document generation with metadata for tracking
    # Metadata is returned in job status and webhook payloads
    job = client.documents.generate_pdf(
        template_id=template["id"],
        variables={
            # Use template's default values or provide your own
            "title": "Example Document",
            "date": "2025-01-30",
        },
        # Optional: attach metadata for tracking/correlation
        metadata={
            "orderId": "ord_12345",
            "customerId": "cust_67890",
            "priority": 1,
        },
    )

    print(f"Job queued: {job['jobId']}")
    print(f"Status: {job['status']}")

    # Wait for completion
    print("Waiting for completion...")
    completed = client.documents.wait_for_completion(
        job["jobId"],
        poll_interval=1.0,
        timeout=60.0,
    )

    if completed["status"] == "completed":
        print("Document generated successfully!")
        print(f"Download URL: {completed['downloadUrl']}")

        # Access metadata from the completed job
        metadata = completed.get("metadata")
        if metadata:
            print(f"Metadata: {metadata}")
            print(f"Order ID: {metadata.get('orderId')}")
    else:
        print(f"Generation failed: {completed.get('errorMessage')}")


if __name__ == "__main__":
    main()
