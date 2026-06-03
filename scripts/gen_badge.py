#!/usr/bin/env python3
"""Generate shields.io-compatible badge JSON for README."""
import json
from pathlib import Path

meta_path = Path("output/meta.json")
if not meta_path.exists():
    print("meta.json not found, skipping badge")
    exit(0)

meta = json.loads(meta_path.read_text())
total = meta.get("total_channels", 0)

badge = {
    "schemaVersion": 1,
    "label": "Live Channels",
    "message": str(total),
    "color": "brightgreen" if total > 0 else "red",
    "style": "flat-square",
    "namedLogo": "youtube-tv",
}

Path("output/badge.json").write_text(json.dumps(badge, indent=2))
print(f"Badge updated: {total} channels")
