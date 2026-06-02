"""
m3u_exporter.py — Export a list of Channel objects to an M3U playlist file.
"""

from pathlib import Path
from scrapers.base import Channel


def export_m3u(channels: list[Channel], output_path: str = "output/playlist.m3u") -> str:
    """
    Write channels to an M3U playlist file.
    Returns the absolute path of the saved file.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    lines = ["#EXTM3U\n"]
    for ch in channels:
        lines.append(ch.to_m3u_entry())

    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"[M3U] Exported {len(channels)} channels → {output_path}")
    return str(Path(output_path).resolve())
