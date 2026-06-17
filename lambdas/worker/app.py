import json
import os
from datetime import UTC, datetime

import boto3

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _complete_document(document_id: str, document_type: str, s3_key: str) -> dict:
    table = dynamodb.Table(os.environ["TABLE_NAME"])
    table.update_item(
        Key={"documentId": document_id},
        UpdateExpression="SET #status = :status, updatedAt = :updatedAt, documentType = :documentType, s3Key = :s3Key",
        ExpressionAttributeNames={"#status": "status"},
        ExpressionAttributeValues={
            ":status": "COMPLETED",
            ":updatedAt": _now(),
            ":documentType": document_type,
            ":s3Key": s3_key,
        },
    )
    return {"documentId": document_id, "status": "COMPLETED"}


def handler(event, context):
    payload = event or {}

    if payload.get("test") == "s3-read":
        key = payload.get("s3Key", "sample.txt")
        response = s3.get_object(Bucket=os.environ["BUCKET_NAME"], Key=key)
        content = response["Body"].read().decode("utf-8")
        return {"test": "s3-read", "content": content}

    if payload.get("Records"):
        results = []
        for record in payload["Records"]:
            body = record.get("body")
            message = json.loads(body) if isinstance(body, str) else body
            results.append(
                _complete_document(
                    message["documentId"],
                    message.get("documentType", "UNKNOWN"),
                    message.get("s3Key", "unknown"),
                )
            )
        return {"processed": results}

    result = _complete_document(
        payload["documentId"],
        payload.get("documentType", "INVOICE"),
        payload.get("s3Key", "manual"),
    )
    return result

