#!/usr/bin/env python3
"""
Webhook Handler Example (Flask)

This example shows how to verify and handle Rynko webhook events,
including accessing custom metadata attached to documents.

Usage:
    pip install flask
    WEBHOOK_SECRET=your_secret python examples/webhook_handler.py

Then send a test webhook:
    curl -X POST http://localhost:5000/webhooks/rynko \
        -H "Content-Type: application/json" \
        -H "X-Rynko-Signature: t=...,v1=..." \
        -d '{"type":"document.completed","id":"evt_123",...}'
"""

import os
from flask import Flask, request, jsonify
from rynko import verify_webhook_signature, WebhookSignatureError

app = Flask(__name__)


@app.route("/webhooks/rynko", methods=["POST"])
def handle_webhook():
    signature = request.headers.get("X-Rynko-Signature")
    payload = request.data.decode("utf-8")

    try:
        event = verify_webhook_signature(
            payload=payload,
            signature=signature,
            secret=os.environ["WEBHOOK_SECRET"],
        )

        print(f"Received: {event['type']} ({event['id']})")

        if event["type"] == "document.completed":
            data = event["data"]
            print(f"Document ready!")
            print(f"  Job ID: {data['jobId']}")
            print(f"  Download URL: {data['downloadUrl']}")

            # Access custom metadata passed in the generate request
            metadata = data.get("metadata")
            if metadata:
                print(f"  Metadata: {metadata}")
                print(f"  Order ID: {metadata.get('orderId')}")
                print(f"  Customer ID: {metadata.get('customerId')}")
                # Use metadata to update your database, trigger workflows, etc.

        elif event["type"] == "document.failed":
            data = event["data"]
            print(f"Document generation failed!")
            print(f"  Job ID: {data['jobId']}")
            print(f"  Error: {data.get('errorMessage')}")
            print(f"  Error Code: {data.get('errorCode')}")

            # Access metadata to identify which order/customer failed
            metadata = data.get("metadata")
            if metadata:
                print(f"  Failed for order: {metadata.get('orderId')}")

        elif event["type"] == "batch.completed":
            data = event["data"]
            print(f"Batch completed!")
            print(f"  Batch ID: {data['batchId']}")
            print(f"  Total: {data['totalJobs']}")
            print(f"  Completed: {data['completedJobs']}")
            print(f"  Failed: {data['failedJobs']}")

            # Access batch-level metadata
            metadata = data.get("metadata")
            if metadata:
                print(f"  Batch run ID: {metadata.get('batchRunId')}")

        return jsonify({"received": True}), 200

    except WebhookSignatureError as e:
        print(f"Invalid signature: {e}")
        return jsonify({"error": "Invalid signature"}), 401

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal error"}), 500


if __name__ == "__main__":
    print("Webhook server listening on http://localhost:5000")
    print("Endpoint: POST /webhooks/rynko")
    print()
    print("Supported event types:")
    print("  - document.completed: Document was successfully generated")
    print("  - document.failed: Document generation failed")
    print("  - batch.completed: Batch of documents completed")
    app.run(port=5000, debug=True)
