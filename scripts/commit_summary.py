#!/usr/bin/env python3
"""Print a short commit summary from meta.json."""
import json, sys
from pathlib import Path

meta_path = Path("output/meta.json")
if not meta_path.exists():
    sys.exit(0)

meta = json.loads(meta_path.read_text())
total   = meta.get("total_channels", "?")
added   = meta.get("added", "?")
removed = meta.get("removed", "?")
updated = meta.get("last_updated", "")

sources = meta.get("sources", {})
src_str = " | ".join(f"{k}: {v}" for k, v in sources.items())

print(f"Total: {total} channels (+{added} new, -{removed} dead)")
print(f"Sources: {src_str}")
print(f"Updated: {updated}")
