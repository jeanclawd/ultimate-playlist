#!/usr/bin/env python3
"""Expand the resolved albums into a track-level playlist.

Reads albums_spotify.csv (written by resolve_spotify.py) and asks Spotify for
the track list of every album that resolved, producing:

    playlist.csv        one row per track, with its Spotify track URI
    playlist_uris.txt   just the URIs, one per line

Those URIs are what any "add to playlist" call needs, whether that is done
through the API with a user token or by pasting into a client.

    python3 build_playlist.py
    python3 build_playlist.py --skip-compilations   # leave out 40+ track sets
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import sys

import resolve_spotify as R

ROOT = pathlib.Path(__file__).resolve().parent


def album_tracks(album_id: str, token: str) -> list[dict]:
    out, offset = [], 0
    while True:
        data = R.api_get(
            f"/albums/{album_id}/tracks",
            {"limit": 50, "offset": offset, "market": "FR"},
            token,
        )
        items = data.get("items", [])
        out.extend(items)
        if len(items) < 50 or not data.get("next"):
            break
        offset += 50
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", default=str(ROOT / "albums_spotify.csv"))
    ap.add_argument("--out", dest="dst", default=str(ROOT / "playlist.csv"))
    ap.add_argument("--uris", default=str(ROOT / "playlist_uris.txt"))
    ap.add_argument("--skip-compilations", action="store_true",
                    help="omit albums of more than 40 tracks")
    args = ap.parse_args()

    env = R.load_env(ROOT / ".env")
    token = R.get_token(env["client_id"], env["client_secret"])

    rows = list(csv.DictReader(open(args.src, newline="", encoding="utf-8")))
    albums = [r for r in rows if r["spotify_album_id"]]
    print(f"{len(albums)} albums to expand")

    tracks, skipped_albums, total_ms = [], [], 0
    for r in albums:
        n = int(r["total_tracks"] or 0)
        if args.skip_compilations and n > 40:
            skipped_albums.append(f"{r['spotify_artist']} — {r['spotify_album']} ({n})")
            continue
        items = album_tracks(r["spotify_album_id"], token)
        print(f"  {r['spotify_artist']} — {r['spotify_album']}: {len(items)} tracks")
        for t in items:
            total_ms += t.get("duration_ms", 0) or 0
            tracks.append({
                "position": len(tracks) + 1,
                "artist": ", ".join(a["name"] for a in t.get("artists", [])),
                "track": t.get("name", ""),
                "album": r["spotify_album"],
                "shelf_artist": r["artist"],
                "shelf_album": r["album"],
                "disc": t.get("disc_number", 1),
                "track_number": t.get("track_number", ""),
                "duration_ms": t.get("duration_ms", ""),
                "spotify_track_uri": t.get("uri", ""),
            })

    if not tracks:
        sys.exit("no tracks — has resolve_spotify.py been run?")

    with open(args.dst, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(tracks[0].keys()))
        w.writeheader()
        w.writerows(tracks)

    with open(args.uris, "w", encoding="utf-8") as f:
        f.write("\n".join(t["spotify_track_uri"] for t in tracks) + "\n")

    hours, rem = divmod(total_ms // 1000, 3600)
    minutes = rem // 60
    print(f"\n{len(tracks)} tracks · {hours}h{minutes:02d}m")
    if skipped_albums:
        print("skipped (compilations):")
        for s in skipped_albums:
            print("  " + s)
    print(f"wrote {args.dst} and {args.uris}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
