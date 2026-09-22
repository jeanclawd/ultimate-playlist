#!/usr/bin/env python3
"""Resolve each album in albums.csv to a Spotify album ID.

Uses the Client Credentials flow, which is enough to search the catalogue.
Credentials come from .env (never committed):

    client_id=...
    client_secret=...

    python3 resolve_spotify.py                  # writes albums_spotify.csv
    python3 resolve_spotify.py --limit 5        # try a few first
    python3 resolve_spotify.py --verbose        # show every candidate considered

Rows identified by artist alone, and unreadable rows, are carried through with
an empty Spotify id and a status saying why — the file stays a complete
inventory of the shelf rather than only the part that matched.
"""

from __future__ import annotations

import argparse
import base64
import csv
import json
import pathlib
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from difflib import SequenceMatcher

ROOT = pathlib.Path(__file__).resolve().parent
API = "https://api.spotify.com/v1"
TOKEN_URL = "https://accounts.spotify.com/api/token"

# A spine is not a catalogue entry. `q` are the searches to try; `title` is the
# name to score candidates against, when the catalogue spells it differently.
OVERRIDES: dict[tuple[str, str], dict] = {
    ("Ed Sheeran", "+ (Plus)"): {"q": ["Ed Sheeran +", "Ed Sheeran Plus"], "title": "+"},
    ("Ed Sheeran", "x (Multiply)"): {"q": ["Ed Sheeran x", "Ed Sheeran Multiply"], "title": "x"},
    ("Phil Collins", "...Hits"): {"q": ["Phil Collins Hits"], "title": "Hits"},
    ("David Bowie", "ChangesBowie"): {"q": ["David Bowie ChangesBowie"], "title": "ChangesBowie"},
    ("Pink Floyd", "A Foot in the Door - The Best of Pink Floyd"): {
        "q": ["Pink Floyd A Foot in the Door The Best of Pink Floyd"],
        "title": "A Foot in the Door: The Best of Pink Floyd",
    },
    ("Creedence Clearwater Revival", "Chronicle"): {
        "q": ["Creedence Clearwater Revival Chronicle 20 Greatest Hits"],
        "title": "Chronicle: 20 Greatest Hits",
    },
    ("Various", "The Real... Jazz"): {"q": ['album:"The Real... Jazz"', "The Real Jazz"]},
    ("Bob Dylan", "The Real... Bob Dylan"): {
        "q": ['artist:"Bob Dylan" album:"The Real..."', "The Real Bob Dylan"]
    },
    ("Various", "Country's Greatest Hits"): {"q": ["Country's Greatest Hits"]},
    ("Jack Johnson", "Sing-A-Longs and Lullabies for the Film Curious George"): {
        "q": ["Jack Johnson Curious George Sing-A-Longs and Lullabies"],
        "title": "Sing-A-Longs & Lullabies For The Film Curious George",
    },
}


# Checked by hand against the catalogue: these are not there, so the search is
# skipped rather than allowed to settle for a near-miss. `substitute` is the
# closest thing that *is* available, resolved and flagged as a substitution.
NOT_ON_SPOTIFY: dict[tuple[str, str], dict] = {
    ("Phil Collins", "...Hits"): {
        "why": "1998 compilation absent from the FR catalogue",
        "substitute": ("Phil Collins", "The Singles"),
    },
    ("David Bowie", "ChangesBowie"): {
        "why": "1990 compilation absent; only ChangesOne/Two/NowBowie are there",
        "substitute": ("David Bowie", "ChangesOneBowie"),
    },
    ("Various", "The Real... Jazz"): {
        "why": "Sony 'The Real...' box set not on Spotify",
    },
    ("Bob Dylan", "The Real... Bob Dylan"): {
        "why": "Sony 'The Real...' box set not on Spotify",
        "substitute": ("Bob Dylan", "The Essential Bob Dylan"),
    },
    ("Nat King Cole", "The Very Best of Nat King Cole"): {
        "why": "this compilation is absent from the FR catalogue",
        "substitute": ("Nat King Cole", "The Nat King Cole Story"),
    },
    ("Richard David Precht", "Wer bin ich - und wenn ja, wie viele?"): {
        "why": "audiobook, not in the music catalogue",
    },
}


def load_env(path: pathlib.Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.exists():
        sys.exit(f"missing {path} — it must define client_id and client_secret")
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def get_token(client_id: str, client_secret: str) -> str:
    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    req = urllib.request.Request(
        TOKEN_URL,
        data=urllib.parse.urlencode({"grant_type": "client_credentials"}).encode(),
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["access_token"]


def api_get(path: str, params: dict, token: str, retries: int = 3):
    url = f"{API}{path}?{urllib.parse.urlencode(params)}"
    for attempt in range(retries):
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:                       # rate limited
                wait = int(e.headers.get("Retry-After", "2")) + 1
                time.sleep(wait)
                continue
            if e.code >= 500 and attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            raise
    raise RuntimeError(f"gave up on {path}")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    for junk in ("...", "…", "(", ")", "[", "]", "-", "–", "'", "'", '"', ",", ".", "!", "&"):
        s = s.replace(junk, " ")
    return " ".join(s.split())


# Edition noise: present in the candidate but never on the spine.
EDITION_NOISE = (
    "deluxe", "deluxe edition", "remaster", "remastered", "expanded",
    "anniversary edition", "special edition", "bonus track version",
    "version", "edition", "explicit", "clean", "reissue",
)


def strip_edition(s: str) -> str:
    out = s
    for w in EDITION_NOISE:
        out = out.replace(f" {w} ", " ")
        if out.endswith(f" {w}"):
            out = out[: -len(w) - 1]
    return " ".join(out.split())


def title_score(want: str, got: str) -> float:
    w, g = norm(want), strip_edition(norm(got))
    if w == g:
        return 1.0
    ratio = SequenceMatcher(None, w, g).ratio()
    # A candidate that contains the wanted title plus extra words (an edition,
    # a volume number) is a weaker match the more it adds.
    if w and w in g:
        extra = len(g) - len(w)
        ratio = max(ratio, 0.95 - min(extra, 40) / 200)
    return ratio


def artist_score(want: str, got: str) -> float:
    w, g = norm(want), norm(got)
    if w == g:
        return 1.0
    # A tribute or karaoke act reads as "<real artist> <something>" and would
    # otherwise look like a perfect containment match. Extra words cost.
    if w and w in g:
        extra_tokens = len(g.split()) - len(w.split())
        return max(0.55, 0.95 - 0.2 * extra_tokens)
    return SequenceMatcher(None, w, g).ratio()


def score(want_artist: str, want_album: str, cand: dict) -> float:
    cand_artist = ", ".join(a["name"] for a in cand.get("artists", []))
    expect = OVERRIDES.get((want_artist, want_album), {}).get("title", want_album)
    a = title_score(expect, cand["name"])
    if want_artist.lower() in ("various", ""):
        s = a
    else:
        # album title carries more signal than the artist string, which is
        # often "Various Artists" or a longer credit list
        s = 0.65 * a + 0.35 * artist_score(want_artist, cand_artist)
    # A one- or two-track "album" is a single or a cover, not the record on the
    # shelf — unless the shelf entry is itself that short.
    if cand.get("total_tracks", 0) <= 2:
        s *= 0.65
    return s


def queries(artist: str, album: str) -> list[str]:
    out = list(OVERRIDES.get((artist, album), {}).get("q", []))
    if artist and artist.lower() != "various":
        out.append(f'artist:"{artist}" album:"{album}"')
        out.append(f"{artist} {album}")
    else:
        out.append(f'album:"{album}"')
        out.append(album)
    return out


def resolve(artist: str, album: str, token: str, verbose: bool) -> tuple[dict | None, float]:
    best, best_score = None, 0.0
    for q in queries(artist, album):
        try:
            data = api_get("/search", {"q": q, "type": "album", "limit": 10, "market": "FR"}, token)
        except urllib.error.HTTPError as e:
            print(f"    search failed ({e.code}) for {q!r}", file=sys.stderr)
            continue
        for cand in data.get("albums", {}).get("items", []):
            s = score(artist, album, cand)
            if verbose:
                names = ", ".join(a["name"] for a in cand.get("artists", []))
                print(f"    {s:.2f}  {names} — {cand['name']}")
            if s > best_score:
                best, best_score = cand, s
        if best_score >= 0.92:                      # good enough, stop early
            break
        time.sleep(0.1)
    return best, best_score


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", default=str(ROOT / "albums.csv"))
    ap.add_argument("--out", dest="dst", default=str(ROOT / "albums_spotify.csv"))
    ap.add_argument("--limit", type=int)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    env = load_env(ROOT / ".env")
    cid, sec = env.get("client_id"), env.get("client_secret")
    if not cid or not sec:
        sys.exit(".env must define both client_id and client_secret")
    token = get_token(cid, sec)

    rows = list(csv.DictReader(open(args.src, newline="", encoding="utf-8")))
    out_rows, done = [], 0
    counts = {
        "matched": 0, "uncertain": 0, "substitute": 0,
        "not_on_spotify": 0, "not_found": 0, "skipped": 0,
    }

    def fill(row: dict, cand: dict, s: float) -> None:
        row.update(
            spotify_album_id=cand["id"],
            spotify_uri=cand["uri"],
            spotify_artist=", ".join(a["name"] for a in cand.get("artists", [])),
            spotify_album=cand["name"],
            release_date=cand.get("release_date", ""),
            total_tracks=str(cand.get("total_tracks", "")),
            match_score=f"{s:.2f}",
        )

    for row in rows:
        artist = (row.get("artist") or "").strip()
        album = (row.get("album") or "").strip()
        conf = (row.get("confidence") or "").strip()
        base = {
            "row": row.get("row", ""),
            "artist": artist,
            "album": album,
            "shelf_confidence": conf,
            "spotify_album_id": "",
            "spotify_uri": "",
            "spotify_artist": "",
            "spotify_album": "",
            "release_date": "",
            "total_tracks": "",
            "match_score": "",
            "status": "",
        }

        if not album:
            base["status"] = "artist only — needs a closer photo" if artist else "unreadable spine"
            counts["skipped"] += 1
            out_rows.append(base)
            continue

        if args.limit is not None and done >= args.limit:
            base["status"] = "not attempted (--limit)"
            out_rows.append(base)
            continue

        print(f"[{done + 1}] {artist} — {album}")
        done += 1

        known = NOT_ON_SPOTIFY.get((artist, album))
        if known:
            sub = known.get("substitute")
            cand, s = resolve(*sub, token, args.verbose) if sub else (None, 0.0)
            if cand and s >= 0.60:
                fill(base, cand, s)
                base["status"] = f"substitute — {known['why']}"
                counts["substitute"] += 1
                print(f"    -> [substitute] {base['spotify_artist']} — {base['spotify_album']}")
            else:
                base["status"] = f"not on Spotify — {known['why']}"
                counts["not_on_spotify"] += 1
                print(f"    -> not on Spotify ({known['why']})")
            out_rows.append(base)
            continue

        cand, s = resolve(artist, album, token, args.verbose)
        if cand and s >= 0.60:
            fill(base, cand, s)
            base["status"] = "matched" if s >= 0.80 else "uncertain — check by hand"
            counts["matched" if s >= 0.80 else "uncertain"] += 1
            print(f"    -> {base['spotify_artist']} — {base['spotify_album']} "
                  f"({base['release_date'][:4]}, {base['total_tracks']} tracks) {s:.2f}")
        else:
            base["status"] = "no match found"
            base["match_score"] = f"{s:.2f}" if cand else ""
            counts["not_found"] += 1
            print("    -> no match")
        out_rows.append(base)

    fields = list(out_rows[0].keys())
    with open(args.dst, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out_rows)

    print("\n" + " · ".join(f"{k}: {v}" for k, v in counts.items()))
    print(f"wrote {args.dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
