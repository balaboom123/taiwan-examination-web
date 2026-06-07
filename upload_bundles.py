import json
import subprocess
import sys
from pathlib import Path

tag = "moex-bundles"
assets = json.loads(Path("data/release-assets.json").read_text(encoding="utf-8"))
total = len(assets)
missing = []
failed = []

for i, asset in enumerate(assets, 1):
    local_path = Path(asset["storage_key"])
    if not local_path.exists():
        missing.append(str(local_path))
        continue
    names = [asset["asset_name"]] + asset.get("legacy_asset_names", [])
    for name in names:
        print(f"[{i}/{total}] {name}")
        result = subprocess.run(
            ["gh", "release", "upload", tag, f"{local_path}#{name}", "--clobber"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"  FAILED: {result.stderr.strip()}")
            failed.append(name)

print(f"\nDone. Uploaded {total - len(missing) - len(failed)}/{total}")
if missing:
    print(f"{len(missing)} files not found locally")
if failed:
    print(f"{len(failed)} uploads failed")
if missing or failed:
    sys.exit(1)
