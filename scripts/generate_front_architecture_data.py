#!/usr/bin/env python3
import json
import base64
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "diagrams" / "official-icons-manifest.json"
OUTPUT_PATH = REPO_ROOT / "frontend" / "data" / "architecture.generated.json"


def terraform_outputs() -> dict:
    result = subprocess.run(
        ["terraform", "-chdir=terraform", "output", "-json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    raw = json.loads(result.stdout)
    return {key: value["value"] for key, value in raw.items()}


def data_uri(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def build_payload(manifest: dict, outputs: dict) -> dict:
    icon_map = {
        entry["service"]: data_uri(REPO_ROOT / entry["local_asset_path"])
        for entry in manifest["icons"]
    }
    return {
        "meta": {
            "title": "iam-operational-serverless-lab",
            "subtitle": "Arquitetura gerada com ícones oficiais da AWS e layout inspirado nas práticas de diagramas AWS",
            "sourcePage": manifest["source"]["page"],
            "sourcePackage": manifest["source"]["package"],
        },
        "deployment": {
            "region": "us-east-1",
            "roleMode": outputs["role_mode"],
            "apiEndpoint": outputs["api_endpoint"],
            "bucketName": outputs["document_bucket_name"],
            "tableName": outputs["document_table_name"],
            "queueUrl": outputs["document_queue_url"],
            "unauthorizedQueueUrl": outputs["unauthorized_queue_url"],
        },
        "services": [
            {
                "id": "api",
                "title": "Amazon API Gateway",
                "subtitle": "Endpoint HTTP",
                "icon": icon_map["Amazon API Gateway"],
                "group": "api",
                "details": [outputs["api_endpoint"], "POST /documents"],
                "x": 120,
                "y": 170,
            },
            {
                "id": "receiver",
                "title": outputs["receiver_function_name"],
                "subtitle": "Recebe payload e grava status inicial",
                "icon": icon_map["AWS Lambda"],
                "group": "api",
                "details": ["status = RECEIVED", "test = s3-list"],
                "x": 120,
                "y": 340,
            },
            {
                "id": "table-a",
                "title": "Amazon DynamoDB",
                "subtitle": outputs["document_table_name"],
                "icon": icon_map["Amazon DynamoDB"],
                "group": "api",
                "details": ["documentId", "status operacional"],
                "x": 120,
                "y": 510,
            },
            {
                "id": "s3",
                "title": "Amazon S3",
                "subtitle": outputs["document_bucket_name"],
                "icon": icon_map["Amazon S3"],
                "group": "async",
                "details": ["entrada de documentos", "trigger por ObjectCreated"],
                "x": 540,
                "y": 170,
            },
            {
                "id": "processor",
                "title": outputs["processor_function_name"],
                "subtitle": "Lê S3, atualiza status e envia SQS",
                "icon": icon_map["AWS Lambda"],
                "group": "async",
                "details": ["test = unauthorized-queue", "status = PROCESSING"],
                "x": 840,
                "y": 170,
            },
            {
                "id": "queue",
                "title": "Amazon SQS",
                "subtitle": "document-processing-queue",
                "icon": icon_map["Amazon SQS"],
                "group": "async",
                "details": [outputs["document_queue_url"], "consumo por event source mapping"],
                "x": 840,
                "y": 380,
            },
            {
                "id": "worker",
                "title": outputs["worker_function_name"],
                "subtitle": "Consome SQS e conclui o fluxo",
                "icon": icon_map["AWS Lambda"],
                "group": "async",
                "details": ["test = s3-read", "status = COMPLETED"],
                "x": 840,
                "y": 590,
            },
            {
                "id": "table-b",
                "title": "Amazon DynamoDB",
                "subtitle": outputs["document_table_name"],
                "icon": icon_map["Amazon DynamoDB"],
                "group": "async",
                "details": ["mesma tabela", "status final"],
                "x": 540,
                "y": 590,
            },
            {
                "id": "iam",
                "title": "IAM Role",
                "subtitle": outputs["role_mode"],
                "icon": icon_map["AWS Identity and Access Management"],
                "group": "ops",
                "details": ["shared-lambda-role no modo atual", "least privilege no modo final"],
                "x": 1220,
                "y": 220,
            },
            {
                "id": "logs",
                "title": "CloudWatch Logs",
                "subtitle": "Observabilidade",
                "icon": icon_map["Amazon CloudWatch Logs"],
                "group": "ops",
                "details": ["receiver, processor, worker", "base para troubleshooting"],
                "x": 1220,
                "y": 470,
            },
        ],
        "groups": [
            {"id": "aws", "title": "AWS Cloud / Mentoring Lab", "x": 40, "y": 40, "w": 1520, "h": 820, "kind": "cloud"},
            {"id": "api-group", "title": "Entrada via API", "x": 80, "y": 120, "w": 380, "h": 610, "kind": "group"},
            {"id": "async-group", "title": "Entrada via S3 e processamento assíncrono", "x": 500, "y": 120, "w": 640, "h": 680, "kind": "group"},
            {"id": "ops-group", "title": "Camadas operacionais", "x": 1180, "y": 120, "w": 300, "h": 620, "kind": "group"},
        ],
        "connectors": [
            {"from": "api", "to": "receiver"},
            {"from": "receiver", "to": "table-a"},
            {"from": "s3", "to": "processor"},
            {"from": "processor", "to": "queue"},
            {"from": "queue", "to": "worker"},
            {"from": "worker", "to": "table-b"},
            {"from": "iam", "to": "receiver", "dashed": True},
            {"from": "iam", "to": "processor", "dashed": True},
            {"from": "iam", "to": "worker", "dashed": True},
            {"from": "logs", "to": "receiver", "dashed": True},
            {"from": "logs", "to": "processor", "dashed": True},
            {"from": "logs", "to": "worker", "dashed": True},
        ],
        "notes": [
            "No modo shared-role, os testes indevidos continuam funcionando.",
            "No modo least-privilege, o fluxo principal continua, mas os testes indevidos devem falhar com AccessDenied.",
        ],
        "officialIcons": [
            {
                "service": entry["service"],
                "officialAssetName": entry["official_asset_name"],
                "localAssetPath": entry["local_asset_path"],
            }
            for entry in manifest["icons"]
        ],
    }


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text())
    outputs = terraform_outputs()
    payload = build_payload(manifest, outputs)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(f"generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
