#!/usr/bin/env python3
"""
Flow Webhook Handler Example (Flask)

This example shows how to verify and handle Flow webhook events,
including run completion, approval, rejection, and delivery failure.

Usage:
    pip install flask
    WEBHOOK_SECRET=your_secret python examples/flow_webhook_handler.py

Then send a test webhook:
    curl -X POST http://localhost:5000/webhooks/flow \
        -H "Content-Type: application/json" \
        -H "X-Rynko-Signature: t=...,v1=..." \
        -d '{"type":"flow.run.completed","id":"evt_123",...}'
"""

import os
from flask import Flask, request, jsonify
from rynko import verify_webhook_signature, WebhookSignatureError

app = Flask(__name__)


@app.route("/webhooks/flow", methods=["POST"])
def handle_flow_webhook():
    signature = request.headers.get("X-Rynko-Signature")
    payload = request.data.decode("utf-8")

    try:
        event = verify_webhook_signature(
            payload=payload,
            signature=signature,
            secret=os.environ["WEBHOOK_SECRET"],
        )

        print(f"Received: {event['type']} ({event['id']})")

        if event["type"] == "flow.run.completed":
            data = event["data"]
            run_id = data.get("runId")
            status = data.get("status")
            print(f"Run completed!")
            print(f"  Run ID: {run_id}")
            print(f"  Status: {status}")

            # Access output data
            output = data.get("output")
            if output:
                print(f"  Output: {output}")

            # Access metadata for correlation
            metadata = data.get("metadata")
            if metadata:
                print(f"  Metadata: {metadata}")
                print(f"  Source: {metadata.get('source')}")

        elif event["type"] == "flow.run.approved":
            data = event["data"]
            print(f"Run approved!")
            print(f"  Run ID: {data.get('runId')}")
            print(f"  Gate ID: {data.get('gateId')}")

            # Access approved output for downstream processing
            output = data.get("output")
            if output:
                print(f"  Approved output: {output}")
                # Use approved output to trigger next steps
                # e.g., generate a document, update a database, etc.

            metadata = data.get("metadata")
            if metadata:
                print(f"  Metadata: {metadata}")

        elif event["type"] == "flow.run.rejected":
            data = event["data"]
            print(f"Run rejected!")
            print(f"  Run ID: {data.get('runId')}")
            print(f"  Gate ID: {data.get('gateId')}")

            # Access validation errors
            errors = data.get("errors", [])
            if errors:
                print(f"  Validation errors:")
                for error in errors:
                    field = error.get("field", "general")
                    print(f"    - [{field}] {error.get('message')}")

            metadata = data.get("metadata")
            if metadata:
                print(f"  Metadata: {metadata}")

        elif event["type"] == "flow.delivery.failed":
            data = event["data"]
            print(f"Delivery failed!")
            print(f"  Delivery ID: {data.get('deliveryId')}")
            print(f"  Run ID: {data.get('runId')}")
            print(f"  URL: {data.get('url')}")
            print(f"  HTTP Status: {data.get('httpStatus')}")
            print(f"  Error: {data.get('error')}")
            print(f"  Attempts: {data.get('attempts')}")

        else:
            print(f"Unhandled event type: {event['type']}")

        return jsonify({"received": True}), 200

    except WebhookSignatureError as e:
        print(f"Invalid signature: {e}")
        return jsonify({"error": "Invalid signature"}), 401

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal error"}), 500


if __name__ == "__main__":
    print("Flow webhook server listening on http://localhost:5000")
    print("Endpoint: POST /webhooks/flow")
    print()
    print("Supported event types:")
    print("  - flow.run.completed: Run finished validation")
    print("  - flow.run.approved: Run was approved")
    print("  - flow.run.rejected: Run was rejected")
    print("  - flow.delivery.failed: Webhook delivery failed")
    app.run(port=5000, debug=True)
