#!/usr/bin/env python3
"""
Webhook Handler Example (Flask)

This example shows how to verify and handle Rynko webhook events.

Usage:
    pip install flask
    WEBHOOK_SECRET=your_secret python examples/webhook_handler.py

Then send a test webhook:
    curl -X POST http://localhost:5000/webhooks/rynko \
        -H "Content-Type: application/json" \
        -H "X-Rynko-Signature: t=...,v1=..." \
        -d '{"type":"document.generated","id":"evt_123",...}'
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

        if event["type"] == "document.generated":
            data = event["data"]
            print(f"Document ready: {data['downloadUrl']}")

        elif event["type"] == "document.failed":
            data = event["data"]
            print(f"Document failed: {data['error']}")

        elif event["type"] == "document.downloaded":
            data = event["data"]
            print(f"Document downloaded: {data['jobId']}")

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
    app.run(port=5000, debug=True)
