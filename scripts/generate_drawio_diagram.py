#!/usr/bin/env python3
import base64
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "diagrams" / "official-icons-manifest.json"
OUTPUT_PATH = REPO_ROOT / "diagrams" / "generated" / "iam-operational-serverless-lab.drawio"


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


def add_cell(root, cell_id, value="", style="", vertex=None, edge=None, parent="1", source=None, target=None, x=0, y=0, w=0, h=0):
    attrs = {"id": cell_id, "parent": str(parent)}
    if value != "":
        attrs["value"] = value
    if style:
        attrs["style"] = style
    if vertex is not None:
        attrs["vertex"] = "1" if vertex else "0"
    if edge is not None:
        attrs["edge"] = "1" if edge else "0"
    if source:
        attrs["source"] = str(source)
    if target:
        attrs["target"] = str(target)

    cell = ET.SubElement(root, "mxCell", attrs)
    if vertex or edge:
        geo_attrs = {"as": "geometry"}
        if edge:
            geo_attrs["relative"] = "1"
            geo = ET.SubElement(cell, "mxGeometry", geo_attrs)
        else:
            geo_attrs.update({"x": str(x), "y": str(y), "width": str(w), "height": str(h)})
            geo = ET.SubElement(cell, "mxGeometry", geo_attrs)
    return cell


def build_diagram(manifest: dict, outputs: dict) -> ET.Element:
    icon_map = {
        entry["service"]: data_uri(REPO_ROOT / entry["local_asset_path"])
        for entry in manifest["icons"]
    }

    mxfile = ET.Element("mxfile", host="app.diagrams.net", modified="2026-06-16T00:00:00.000Z", agent="Codex", version="24.7.17")
    diagram = ET.SubElement(mxfile, "diagram", id="aws-lab", name="AWS Lab")
    model = ET.SubElement(
        diagram,
        "mxGraphModel",
        dx="1600",
        dy="980",
        grid="1",
        gridSize="10",
        guides="1",
        tooltips="1",
        connect="1",
        arrows="1",
        fold="1",
        page="1",
        pageScale="1",
        pageWidth="1600",
        pageHeight="980",
        math="0",
        shadow="0",
    )
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")

    add_cell(
        root, "cloud", "AWS Cloud / Mentoring Lab",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#f2f7ff;strokeColor=#8cb3ff;fontStyle=1;fontSize=18;align=left;spacingLeft=20;spacingTop=14;",
        vertex=True, parent="1", x=40, y=40, w=1520, h=820
    )
    add_cell(
        root, "group_api", "Entrada via API",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8fbff;strokeColor=#d4dce6;fontStyle=1;fontSize=16;align=left;spacingLeft=16;spacingTop=12;",
        vertex=True, parent="1", x=80, y=120, w=380, h=610
    )
    add_cell(
        root, "group_async", "Entrada via S3 e processamento assíncrono",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8fbff;strokeColor=#d4dce6;fontStyle=1;fontSize=16;align=left;spacingLeft=16;spacingTop=12;",
        vertex=True, parent="1", x=500, y=120, w=640, h=680
    )
    add_cell(
        root, "group_ops", "Camadas operacionais",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8fbff;strokeColor=#d4dce6;fontStyle=1;fontSize=16;align=left;spacingLeft=16;spacingTop=12;",
        vertex=True, parent="1", x=1180, y=120, w=300, h=620
    )

    services = [
        ("api", "Amazon API Gateway", outputs["api_endpoint"], icon_map["Amazon API Gateway"], 140, 180),
        ("receiver", outputs["receiver_function_name"], "status = RECEIVED", icon_map["AWS Lambda"], 140, 350),
        ("table_a", "DynamoDB DocumentProcessing", "estado inicial", icon_map["Amazon DynamoDB"], 140, 520),
        ("s3", f"S3 {outputs['document_bucket_name']}", "ObjectCreated trigger", icon_map["Amazon S3"], 560, 180),
        ("processor", outputs["processor_function_name"], "PROCESSING + SQS", icon_map["AWS Lambda"], 860, 180),
        ("queue", "SQS document-processing-queue", "event source mapping", icon_map["Amazon SQS"], 860, 390),
        ("worker", outputs["worker_function_name"], "status = COMPLETED", icon_map["AWS Lambda"], 860, 600),
        ("table_b", "DynamoDB DocumentProcessing", "estado final", icon_map["Amazon DynamoDB"], 560, 600),
        ("iam", f"IAM Role ({outputs['role_mode']})", "shared-role ou least privilege", icon_map["AWS Identity and Access Management"], 1220, 220),
        ("logs", "CloudWatch Logs", "receiver / processor / worker", icon_map["Amazon CloudWatch Logs"], 1220, 470),
    ]

    for cell_id, title, subtitle, icon, x, y in services:
        add_cell(
            root, f"{cell_id}_card", "",
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6dee8;shadow=1;",
            vertex=True, parent="1", x=x, y=y, w=240, h=110
        )
        add_cell(
            root, f"{cell_id}_icon", "",
            f"shape=image;imageAspect=0;aspect=fixed;verticalLabelPosition=bottom;verticalAlign=top;image={icon};",
            vertex=True, parent="1", x=x+16, y=y+22, w=48, h=48
        )
        add_cell(
            root, f"{cell_id}_title", title,
            "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontStyle=1;fontSize=14;",
            vertex=True, parent="1", x=x+74, y=y+20, w=150, h=24
        )
        add_cell(
            root, f"{cell_id}_subtitle", subtitle,
            "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;fontSize=12;fontColor=#526171;whiteSpace=wrap;",
            vertex=True, parent="1", x=x+74, y=y+46, w=150, h=40
        )

    edges = [
        ("e1", "api_card", "receiver_card", False),
        ("e2", "receiver_card", "table_a_card", False),
        ("e3", "s3_card", "processor_card", False),
        ("e4", "processor_card", "queue_card", False),
        ("e5", "queue_card", "worker_card", False),
        ("e6", "worker_card", "table_b_card", False),
        ("e7", "iam_card", "receiver_card", True),
        ("e8", "iam_card", "processor_card", True),
        ("e9", "iam_card", "worker_card", True),
        ("e10", "logs_card", "receiver_card", True),
        ("e11", "logs_card", "processor_card", True),
        ("e12", "logs_card", "worker_card", True),
    ]

    for edge_id, source, target, dashed in edges:
        style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;strokeWidth=2;"
        if dashed:
            style += "dashed=1;dashPattern=8 8;"
        add_cell(root, edge_id, "", style, edge=True, parent="1", source=source, target=target)

    add_cell(
        root, "footer",
        "Ícones oficiais AWS + ambiente atual do Terraform | shared-role no deployment atual",
        "text;html=1;strokeColor=none;fillColor=none;align=left;fontSize=12;fontColor=#5f6b7a;",
        vertex=True, parent="1", x=80, y=890, w=700, h=24
    )

    return mxfile


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text())
    outputs = terraform_outputs()
    mxfile = build_diagram(manifest, outputs)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(ET.tostring(mxfile, encoding="unicode"))
    print(f"generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
