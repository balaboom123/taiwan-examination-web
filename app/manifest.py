from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

SUPPORTED_SCHEMA_VERSION = 1


@dataclass
class SourceManifest:
    schema_version: int = SUPPORTED_SCHEMA_VERSION
    probe_policy: dict[str, Any] = field(default_factory=dict)
    years: dict[str, dict[str, Any]] = field(default_factory=dict)
    exams: dict[str, dict[str, Any]] = field(default_factory=dict)
    files: dict[str, dict[str, Any]] = field(default_factory=dict)


def load_source_manifest(path: Path) -> SourceManifest:
    if not path.exists():
        return SourceManifest()
    data = json.loads(path.read_text(encoding="utf-8"))
    schema_version = data.get("schema_version")
    if schema_version != SUPPORTED_SCHEMA_VERSION:
        raise ValueError(f"Unsupported source manifest schema_version: {schema_version}")
    return SourceManifest(
        schema_version=schema_version,
        probe_policy=data.get("probe_policy", {}),
        years=data.get("years", {}),
        exams=data.get("exams", {}),
        files=data.get("files", {}),
    )


def write_source_manifest(path: Path, manifest: SourceManifest) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(asdict(manifest), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
