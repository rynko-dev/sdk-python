#!/usr/bin/env python3
"""
Error Handling Example

This example shows how to handle errors from the Rynko API.

Usage:
    RYNKO_API_KEY=your_key python examples/error_handling.py
"""

import os
from rynko import Rynko, RynkoError


def main():
    client = Rynko(api_key=os.environ["RYNKO_API_KEY"])

    # Example 1: Template not found
    print("\n--- Example 1: Template not found ---")
    try:
        client.templates.get("non-existent-template-id")
    except RynkoError as e:
        print(f"Error: {e.message}")
        print(f"Code: {e.code}")
        print(f"Status: {e.status_code}")

    # Example 2: Invalid API key
    print("\n--- Example 2: Invalid API key ---")
    bad_client = Rynko(api_key="invalid-key")
    try:
        bad_client.me()
    except RynkoError as e:
        print(f"Error: {e.message}")
        print(f"Code: {e.code}")

    # Example 3: Handling specific error codes
    print("\n--- Example 3: Handling specific error codes ---")
    try:
        client.documents.generate_pdf(
            template_id="invalid-id",
            variables={},
        )
    except RynkoError as e:
        if e.code == "ERR_TMPL_001":
            print("Template not found - check the template ID")
        elif e.code == "ERR_TMPL_003":
            print("Template validation failed - check your variables")
        elif e.code == "ERR_QUOTA_001":
            print("Quota exceeded - upgrade your plan")
        elif e.code in ("ERR_AUTH_001", "ERR_AUTH_004"):
            print("Authentication failed - check your API key")
        else:
            print(f"Unexpected error: {e.message}")


if __name__ == "__main__":
    main()
