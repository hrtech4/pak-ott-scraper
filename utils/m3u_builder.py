"""
M3U Playlist Builder
Generates standard M3U playlists from channel dicts.
"""

from datetime import datetime, timezone
from pathlib import Path


class M3UBuilder:
    @staticmethod
    def write(channels: list, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            "#EXTM3U",
            f'# Generated: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}',
            f"# Channels: {len(channels)}",
            f"# Sources: Tamasha, Tapmad, MyCo, ShoqPK",
            "",
        ]

        for ch in channels:
            name   = ch.get("name", "Unknown")
            url    = ch.get("url", "")
            logo   = ch.get("logo", "")
            group  = ch.get("group", "General")
            lang   = ch.get("language", "Urdu")
            country = ch.get("country", "PK")
            source = ch.get("source", "")

            attrs = (
                f'#EXTINF:-1 tvg-name="{name}" '
                f'tvg-logo="{logo}" '
                f'group-title="{group}" '
                f'tvg-language="{lang}" '
                f'tvg-country="{country}" '
                f'tvg-source="{source}"'
                f',{name}'
            )
            lines.append(attrs)
            lines.append(url)
            lines.append("")

        path.write_text("\n".join(lines), encoding="utf-8")

    @staticmethod
    def to_string(channels: list) -> str:
        tmp_path = Path("/tmp/_m3u_tmp.m3u")
        M3UBuilder.write(channels, tmp_path)
        return tmp_path.read_text()
