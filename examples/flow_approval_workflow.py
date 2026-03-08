#!/usr/bin/env python3
"""
Flow Approval Workflow Example

This example shows how to programmatically list and process pending
Flow approvals. Useful for building automated approval pipelines.

Usage:
    RYNKO_API_KEY=your_key python examples/flow_approval_workflow.py
"""

import os
from rynko import Rynko, RynkoError


def main():
    client = Rynko(api_key=os.environ["RYNKO_API_KEY"])

    # Verify authentication
    user = client.me()
    print(f"Authenticated as: {user['email']}")

    # List pending approvals
    print("\nFetching pending approvals...")
    result = client.flow.list_approvals(status="pending", limit=50)
    approvals = result["data"]
    total = result["meta"]["total"]

    print(f"Found {len(approvals)} pending approvals (total: {total})")

    if not approvals:
        print("No pending approvals to process.")
        return

    # Process each pending approval
    approved_count = 0
    rejected_count = 0
    skipped_count = 0

    for approval in approvals:
        approval_id = approval["id"]
        run_id = approval["run_id"]

        # Get the run details to make an approval decision
        print(f"\n--- Approval {approval_id} ---")
        print(f"  Run ID: {run_id}")

        try:
            run = client.flow.get_run(run_id)
        except RynkoError as e:
            print(f"  Failed to get run details: {e.message}")
            skipped_count += 1
            continue

        run_input = run.get("input", {})
        run_metadata = run.get("metadata", {})

        print(f"  Gate ID: {run.get('gate_id')}")
        print(f"  Input: {run_input}")
        if run_metadata:
            print(f"  Metadata: {run_metadata}")

        # Example approval logic:
        # Auto-approve if amount is under threshold, reject otherwise
        amount = run_input.get("amount", run_input.get("invoice_amount", 0))

        if isinstance(amount, (int, float)) and amount > 10000:
            # Reject high-value items for manual review
            print(f"  Decision: REJECT (amount {amount} exceeds threshold)")
            try:
                client.flow.reject(
                    approval_id,
                    reason=f"Amount {amount} exceeds auto-approval threshold of 10000",
                )
                rejected_count += 1
            except RynkoError as e:
                print(f"  Failed to reject: {e.message}")
                skipped_count += 1
        else:
            # Auto-approve low-value items
            print(f"  Decision: APPROVE")
            try:
                client.flow.approve(
                    approval_id,
                    note="Auto-approved by SDK approval workflow",
                )
                approved_count += 1
            except RynkoError as e:
                print(f"  Failed to approve: {e.message}")
                skipped_count += 1

    # Print summary
    print(f"\n--- Summary ---")
    print(f"  Approved: {approved_count}")
    print(f"  Rejected: {rejected_count}")
    print(f"  Skipped:  {skipped_count}")
    print(f"  Total:    {len(approvals)}")


if __name__ == "__main__":
    main()
