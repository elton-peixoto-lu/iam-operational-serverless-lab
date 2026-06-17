import json
import os
import urllib.parse
from datetime import UTC, datetime

import boto3

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")
sqs = boto3.client("sqs")


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _send_for_processing(document_id: str, s3_key: str, document_type: str) -> dict:
    table = dynamodb.Table(os.environ["TABLE_NAME"])
    queue_url = os.environ["QUEUE_URL"]
    bucket_name = os.environ["BUCKET_NAME"]

    obj = s3.get_object(Bucket=bucket_name, Key=s3_key)
    metadata = obj.get("Metadata", {})
    resolved_document_id = metadata.get("document-id", document_id)
    resolved_document_type = metadata.get("document-type", document_type)

    table.update_item(
        Key={"documentId": resolved_document_id},
        UpdateExpression="SET #status = :status, updatedAt = :updatedAt, documentType = :documentType, s3Key = :s3Key",
        ExpressionAttributeNames={"#status": "status"},
        ExpressionAttributeValues={
            ":status": "PROCESSING",
            ":updatedAt": _now(),
            ":documentType": resolved_document_type,
            ":s3Key": s3_key,
        },
    )

    message = {
        "documentId": resolved_document_id,
        "documentType": resolved_document_type,
        "s3Key": s3_key,
    }
    sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(message))
    return message


def handler(event, context):
    payload = event or {}

    if payload.get("test") == "unauthorized-queue":
        unauthorized_queue_url = os.environ["UNAUTHORIZED_QUEUE_URL"]
        sqs.send_message(
            QueueUrl=unauthorized_queue_url,
            MessageBody=json.dumps({"message": "should be denied under least privilege"}),
        )
        return {"result": "sent-to-unauthorized-queue"}

    if payload.get("Records") and payload["Records"][0].get("eventSource") == "aws:s3":
        results = []
        for record in payload["Records"]:
            bucket_name = record["s3"]["bucket"]["name"]
            key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])
            obj = s3.get_object(Bucket=bucket_name, Key=key)
            metadata = obj.get("Metadata", {})
            document_id = metadata.get("document-id", key)
            document_type = metadata.get("document-type", "UNKNOWN")
            results.append(_send_for_processing(document_id, key, document_type))
        return {"processed": results}

    document_id = payload["documentId"]
    s3_key = payload["s3Key"]
    document_type = payload.get("documentType", "INVOICE")
    result = _send_for_processing(document_id, s3_key, document_type)
    return {"processed": result}

