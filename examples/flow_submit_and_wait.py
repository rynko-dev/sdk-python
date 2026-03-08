#!/usr/bin/env python3
"""
Flow Submit and Wait Example

This example shows how to submit a run to a Flow gate and wait for
the validation result. This is the core Flow workflow.

Usage:
    RYNKO_API_KEY=your_key python examples/flow_submit_and_wait.py
"""

import os
from rynko import Rynko


def main():
    client = Rynko(api_key=os.environ["RYNKO_API_KEY"])

    # Verify authentication
    user = client.me()
    print(f"Authenticated as: {user['email']}")

    # List gates and pick the first published one
    result = client.flow.list_gates(status="published")
    gates = result["data"]
    if not gates:
        print("No published gates found. Create and publish a gate first.")
        return

    gate = gates[0]
    print(f"Using gate: {gate['name']} ({gate['id']})")

    # Submit a run with sample input and metadata
    print("\nSubmitting run...")
    run = client.flow.submit_run(
        gate["id"],
        input={
            "customer_name": "Acme Corporation",
            "invoice_amount": 1500.00,
            "currency": "USD",
            "line_items": [
                {"description": "Consulting services", "amount": 1000.00},
                {"description": "Implementation fee", "amount": 500.00},
            ],
        },
        metadata={
            "source": "sdk-example",
            "environment": "development",
        },
    )

    print(f"Run ID: {run['id']}")
    print(f"Status: {run['status']}")

    # Wait for the run to complete
    print("\nWaiting for validation result...")
    completed = client.flow.wait_for_run(
        run["id"],
        poll_interval=1.0,
        timeout=120.0,
    )

    print(f"\nFinal status: {completed['status']}")

    # Handle the outcome
    if completed["status"] == "approved":
        print("Run approved!")
        if completed.get("output"):
            print(f"Output: {completed['output']}")

    elif completed["status"] == "rejected":
        print("Run rejected.")
        if completed.get("errors"):
            print("Validation errors:")
            for error in completed["errors"]:
                field = error.get("field", "general")
                print(f"  - [{field}] {error['message']}")

    elif completed["status"] == "review_required":
        print("Run requires human review.")
        print("Check the Rynko dashboard for pending approvals.")

    elif completed["status"] in ("validation_failed", "render_failed", "delivery_failed"):
        print(f"Run failed with status: {completed['status']}")
        if completed.get("errors"):
            for error in completed["errors"]:
                print(f"  - {error['message']}")

    else:
        print(f"Unexpected status: {completed['status']}")


if __name__ == "__main__":
    main()
