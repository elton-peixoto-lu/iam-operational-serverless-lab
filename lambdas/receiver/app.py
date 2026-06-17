import json
import os
from datetime import UTC, datetime

import boto3

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")


def _response(status_code: int, payload: dict) -> dict:
    return {"statusCode": status_code, "body": json.dumps(payload)}


def _extract_payload(event: dict) -> dict:
    if "body" in event:
        body = event.get("body") or "{}"
        return json.loads(body) if isinstance(body, str) else body
    return event


def handler(event, context):
    payload = _extract_payload(event or {})

    if payload.get("test") == "s3-list":
        buckets = s3.list_buckets()
        names = [bucket["Name"] for bucket in buckets.get("Buckets", [])]
        return _response(200, {"test": "s3-list", "buckets": names})

    document_id = payload["documentId"]
    document_type = payload["documentType"]
    now = datetime.now(UTC).isoformat()

    table = dynamodb.Table(os.environ["TABLE_NAME"])
    table.put_item(
        Item={
            "documentId": document_id,
            "documentType": document_type,
            "status": "RECEIVED",
            "createdAt": now,
            "updatedAt": now,
        }
    )

    return _response(
        200,
        {
            "message": "receiver stored document",
            "documentId": document_id,
            "documentType": document_type,
            "status": "RECEIVED",
        },
    )

