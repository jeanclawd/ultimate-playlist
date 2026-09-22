#!/usr/bin/env python3
"""Build docs/data.json — everything the browser app needs, in one file.

Combines albums_spotify.csv and playlist.csv, and fetches cover art for each
resolved album so the shelf can be browsed visually.

    python3 build_site_data.py
"""

from __future__ import annotations

import collections
import csv
import json
import pathlib

import resolve_spotify as R

ROOT = pathlib.Path(__file__).resolve().parent
DOCS = ROOT / "docs"


def covers(ids: list[str], token: str) -> dict[str, str]:
    """album id -> medium cover url, 20 ids per request."""
    out: dict[str, str] = {}
    for i in range(0, len(ids), 20):
        chunk = [x for x in ids[i:i + 20] if x]
        if not chunk:
            continue
        data = R.api_get("/albums", {"ids": ",".join(chunk), "market": "FR"}, token)
        for alb in data.get("albums", []):
            if not alb:
                continue
            imgs = sorted(alb.get("images", []), key=lambda im: im.get("width", 0))
            # the middle size: big enough for a grid, small enough to load fast
            pick = imgs[len(imgs) // 2] if imgs else None
            if pick:
                out[alb["id"]] = pick["url"]
    return out


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    albums = list(csv.DictReader(open(ROOT / "albums_spotify.csv", encoding="utf-8")))
    tracks = list(csv.DictReader(open(ROOT / "playlist.csv", encoding="utf-8")))

    by_album: dict[tuple[str, str], list] = collections.defaultdict(list)
    for t in tracks:
        by_album[(t["shelf_artist"], t["shelf_album"])].append({
            "n": t["track"],
            "a": t["artist"],
            "d": int(t["duration_ms"] or 0),
            "u": t["spotify_track_uri"],
        })

    env = R.load_env(ROOT / ".env")
    token = R.get_token(env["client_id"], env["client_secret"])
    art = covers([a["spotify_album_id"] for a in albums if a["spotify_album_id"]], token)
    print(f"cover art for {len(art)} albums")

    out = []
    for a in albums:
        if not a["album"]:
            continue
        out.append({
            "row": int(a["row"]),
            "artist": a["artist"],
            "album": a["album"],
            "status": a["status"],
            "spotify_id": a["spotify_album_id"],
            "spotify_artist": a["spotify_artist"],
            "spotify_album": a["spotify_album"],
            "year": (a["release_date"] or "")[:4],
            "art": art.get(a["spotify_album_id"], ""),
            "tracks": by_album.get((a["artist"], a["album"]), []),
        })

    data = {
        "generated": "2026-09-22",
        "albums": out,
        "unidentified": [
            {"row": int(a["row"]), "artist": a["artist"], "note": a["status"]}
            for a in albums if not a["album"]
        ],
        "totals": {
            "albums": len(out),
            "with_spotify": sum(1 for a in out if a["spotify_id"]),
            "tracks": sum(len(a["tracks"]) for a in out),
            "duration_ms": sum(t["d"] for a in out for t in a["tracks"]),
        },
    }
    path = DOCS / "data.json"
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    ms = data["totals"]["duration_ms"]
    print(f"{data['totals']['albums']} albums · {data['totals']['tracks']} tracks · "
          f"{ms // 3600000}h{ms % 3600000 // 60000:02d}m")
    print(f"wrote {path} ({path.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
