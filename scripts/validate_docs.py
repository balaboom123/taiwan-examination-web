from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.cli import build_parser
from app.providers.registry import _PROVIDER_FACTORIES
from app.site_registry import get_site_config
from scripts.render_docs import PROVIDER_END, expected_outputs


STATUS_VALUES = {"covered", "partial", "blocked"}
PROVIDER_SECTIONS = [
    "Source boundary",
    "Gaps and blockers",
    "Publication shape",
    "Operating it",
    "Open decisions",
]
REQUIRED_PATHS = [
    "AGENTS.md",
    "docs/architecture.md",
    "docs/concepts.md",
    "docs/reference/exam-identity.md",
    "docs/reference/contracts.md",
    "docs/contributing/add-a-provider.md",
    "docs/operations/commands.md",
    "docs/providers/README.md",
    "docs/providers/rejected-sources.md",
]
FORBIDDEN_LIVE_DIRS = ["docs/developer", "docs/operator", "docs/superpowers"]
INLINE_LINK = re.compile(r"!?\[[^\]]*\]\((?P<target><[^>]+>|[^)\s]+)(?:\s+[^)]*)?\)")
REFERENCE_LINK = re.compile(r"^\s*\[[^\]]+\]:\s*(?P<target>\S+)", flags=re.MULTILINE)


def _load_inventory(repo_root: Path) -> dict[str, object]:
    return json.loads((repo_root / "catalog" / "source-inventory.json").read_text(encoding="utf-8"))


def _frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    try:
        raw = text.split("---\n", 2)[1]
    except IndexError:
        return {}
    fields: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


def _cli_commands() -> set[str]:
    parser = build_parser()
    subparsers_action = next(action for action in parser._actions if action.dest == "command")
    return set(subparsers_action.choices)


def _validate_provider_pages(repo_root: Path, inventory: dict[str, object]) -> list[str]:
    errors: list[str] = []
    provider_root = repo_root / "docs" / "providers"
    inventory_by_id = {entry["provider_id"]: entry for entry in inventory["providers"]}
    page_paths = {
        path.stem: path
        for path in provider_root.glob("*.md")
        if path.name not in {"README.md", "rejected-sources.md"}
    }
    inventory_ids = set(inventory_by_id)
    registry_ids = set(_PROVIDER_FACTORIES)
    site_ids = set(get_site_config(str(inventory["site_id"])).provider_ids)
    page_ids = set(page_paths)
    for label, actual in (("runtime registry", registry_ids), ("site registry", site_ids), ("provider pages", page_ids)):
        missing = sorted(inventory_ids - actual)
        extra = sorted(actual - inventory_ids)
        if missing or extra:
            errors.append(f"inventory/{label} mismatch: missing={missing} extra={extra}")

    for provider_id, path in sorted(page_paths.items()):
        if provider_id not in inventory_by_id:
            continue
        text = path.read_text(encoding="utf-8")
        fields = _frontmatter(text)
        expected_fields = {
            "provider_id": provider_id,
            "status": str(inventory_by_id[provider_id]["status"]),
            "site": str(inventory["site_id"]),
            "last_verified": str(inventory["captured_at"]),
        }
        if fields != expected_fields:
            errors.append(f"{path.relative_to(repo_root)}: frontmatter {fields!r} != {expected_fields!r}")
        if fields.get("status") not in STATUS_VALUES:
            errors.append(f"{path.relative_to(repo_root)}: invalid provider status {fields.get('status')!r}")
        sections = re.findall(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE)
        if sections != PROVIDER_SECTIONS:
            errors.append(f"{path.relative_to(repo_root)}: expected sections {PROVIDER_SECTIONS!r}, found {sections!r}")
        body = text.split(PROVIDER_END, 1)[1] if PROVIDER_END in text else text
        for url in inventory_by_id[provider_id]["official_source_urls"]:
            if url in body:
                errors.append(f"{path.relative_to(repo_root)}: official URL is duplicated outside the generated block")
    return errors


def _relative_link_errors(repo_root: Path) -> list[str]:
    errors: list[str] = []
    markdown_paths = list((repo_root / "docs").rglob("*.md")) + [repo_root / "README.md", repo_root / "AGENTS.md"]
    for path in markdown_paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        targets = [match.group("target") for match in INLINE_LINK.finditer(text)]
        targets.extend(match.group("target") for match in REFERENCE_LINK.finditer(text))
        for raw_target in targets:
            target = raw_target.strip("<>")
            if target.startswith(("http://", "https://", "mailto:", "data:", "#")):
                continue
            target_path = unquote(target.split("#", 1)[0])
            if not target_path:
                continue
            resolved = (repo_root / target_path.lstrip("/")) if target_path.startswith("/") else (path.parent / target_path)
            if not resolved.exists():
                errors.append(f"{path.relative_to(repo_root)}: broken relative link {raw_target!r}")
    return errors


def _live_markdown(repo_root: Path) -> list[Path]:
    return [path for path in (repo_root / "docs").rglob("*.md") if "archive" not in path.relative_to(repo_root / "docs").parts]


def _documentation_hygiene_errors(repo_root: Path, inventory: dict[str, object]) -> list[str]:
    errors: list[str] = []
    commands = _cli_commands()
    for path in _live_markdown(repo_root) + [repo_root / "README.md", repo_root / "AGENTS.md"]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if "\\n\\n" in text:
            errors.append(f"{path.relative_to(repo_root)}: contains literal \\n\\n")
        headings = re.findall(r"^#{1,6}\s+(.+?)\s*$", text, flags=re.MULTILINE)
        duplicates = sorted(heading for heading, count in Counter(headings).items() if count > 1)
        if duplicates:
            errors.append(f"{path.relative_to(repo_root)}: duplicate headings {duplicates}")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if re.search(r"(?<!uv run )python3? -m app\b", line):
                errors.append(f"{path.relative_to(repo_root)}:{line_number}: use 'uv run python -m app'")
            if "cmd /c" in line.lower() or line.rstrip().endswith("^"):
                errors.append(f"{path.relative_to(repo_root)}:{line_number}: Windows command syntax is not allowed")
            match = re.search(r"(?:uv run )?python3? -m app\s+([a-z0-9-]+)", line)
            if match and match.group(1) not in commands:
                errors.append(f"{path.relative_to(repo_root)}:{line_number}: unknown app subcommand {match.group(1)!r}")
    for forbidden in FORBIDDEN_LIVE_DIRS:
        if (repo_root / forbidden).exists():
            errors.append(f"legacy live documentation directory still exists: {forbidden}")
    for required in REQUIRED_PATHS:
        if not (repo_root / required).is_file():
            errors.append(f"required documentation is missing: {required}")
    for entry in [*inventory["providers"], *inventory["candidates"]]:
        for evidence in entry["evidence"]:
            if evidence.startswith(("http://", "https://")):
                continue
            if evidence.startswith("docs/archive/"):
                errors.append(f"{entry.get('provider_id', entry.get('source_id'))}: archive path used as inventory evidence: {evidence}")
            if not (repo_root / evidence).exists():
                errors.append(f"{entry.get('provider_id', entry.get('source_id'))}: missing inventory evidence: {evidence}")
    return errors


def _freshness_errors(repo_root: Path) -> list[str]:
    errors: list[str] = []
    try:
        outputs = expected_outputs(repo_root)
    except ValueError as exc:
        return [f"cannot render documentation: {exc}"]
    for path, expected in outputs.items():
        if not path.exists():
            errors.append(f"missing generated documentation: {path.relative_to(repo_root)}")
        elif path.read_text(encoding="utf-8") != expected:
            errors.append(f"stale generated documentation: {path.relative_to(repo_root)}")
    return errors


def validate(repo_root: Path) -> list[str]:
    inventory = _load_inventory(repo_root)
    errors: list[str] = []
    errors.extend(_validate_provider_pages(repo_root, inventory))
    errors.extend(_documentation_hygiene_errors(repo_root, inventory))
    errors.extend(_relative_link_errors(repo_root))
    errors.extend(_freshness_errors(repo_root))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate maintained documentation against executable repository truth.")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true", help="Explicitly select non-mutating validation mode.")
    args = parser.parse_args()
    errors = validate(args.repo_root)
    if errors:
        for error in errors:
            print(f"docs validation failed: {error}", file=sys.stderr)
        return 1
    print("documentation validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
