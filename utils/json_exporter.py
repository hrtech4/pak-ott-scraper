"""
json_exporter.py — Export a list of Channel objects to a JSON file.
"""

import json
from pathlib import Path
from scrapers.base import Channel


def export_json(channels: list[Channel], output_path: str = "output/channels.json") -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    data = [ch.to_dict() for ch in channels]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"[JSON] Exported {len(channels)} channels → {output_path}")
    return str(Path(output_path).resolve())
