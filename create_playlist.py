#!/usr/bin/env python3
"""Create the playlist on your Spotify account from playlist_uris.txt.

The other two scripts use the Client Credentials flow, which can read the
catalogue but cannot touch an account. Writing a playlist needs *you* to
authorise the app once, so this script runs the Authorization Code flow:
it opens a URL, you approve, Spotify redirects back to a local server.

One-time setup, in the Spotify developer dashboard for this app:

    Settings -> Redirect URIs -> add   http://127.0.0.1:8888/callback

Then:

    python3 create_playlist.py --name "Ultimate Playlist"
    python3 create_playlist.py --name "..." --public     # default is private
    python3 create_playlist.py --dry-run                 # show what it would add

If the machine running this has no browser, copy the printed URL to any
browser; the redirect target is on this machine, so run it where you can
reach 127.0.0.1 — or use --manual to paste the redirected URL back in.
"""

from __future__ import annotations

import argparse
import base64
import http.server
import json
import pathlib
import secrets
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

import resolve_spotify as R

ROOT = pathlib.Path(__file__).resolve().parent
REDIRECT = "http://127.0.0.1:8888/callback"
SCOPES = "playlist-modify-private playlist-modify-public"
BATCH = 100                      # Spotify accepts 100 URIs per add call


class _Handler(http.server.BaseHTTPRequestHandler):
    code: str | None = None
    state: str | None = None

    def do_GET(self):                                    # noqa: N802
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        _Handler.code = (q.get("code") or [None])[0]
        _Handler.state = (q.get("state") or [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        ok = _Handler.code is not None
        self.wfile.write(
            b"<h2>Authorised - you can close this tab.</h2>" if ok
            else b"<h2>No code returned.</h2>"
        )

    def log_message(self, *a):                           # keep the console quiet
        pass


def authorise(client_id: str, client_secret: str, manual: bool) -> str:
    state = secrets.token_urlsafe(16)
    url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode({
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": REDIRECT,
        "scope": SCOPES,
        "state": state,
    })

    if manual:
        print("Open this URL, approve, then paste the full redirected URL here:\n")
        print(url + "\n")
        back = input("redirected URL: ").strip()
        q = urllib.parse.parse_qs(urllib.parse.urlparse(back).query)
        code = (q.get("code") or [None])[0]
        if (q.get("state") or [None])[0] != state:
            sys.exit("state mismatch — start again")
    else:
        server = http.server.HTTPServer(("127.0.0.1", 8888), _Handler)
        threading.Thread(target=server.handle_request, daemon=True).start()
        print("Opening the approval page:\n" + url + "\n")
        try:
            webbrowser.open(url)
        except Exception:
            pass
        print("waiting for the redirect on 127.0.0.1:8888 ...")
        for _ in range(600):                              # ~2 minutes
            if _Handler.code:
                break
            threading.Event().wait(0.2)
        code = _Handler.code
        if _Handler.state != state:
            sys.exit("state mismatch — start again")

    if not code:
        sys.exit("no authorisation code received")

    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    req = urllib.request.Request(
        R.TOKEN_URL,
        data=urllib.parse.urlencode({
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT,
        }).encode(),
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["access_token"]


def api_post(path: str, body: dict, token: str) -> dict:
    req = urllib.request.Request(
        f"{R.API}{path}",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="Ultimate Playlist")
    ap.add_argument("--description", default="Reconstructed from the CD shelf")
    ap.add_argument("--uris", default=str(ROOT / "playlist_uris.txt"))
    ap.add_argument("--public", action="store_true")
    ap.add_argument("--manual", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    uris = [u.strip() for u in pathlib.Path(args.uris).read_text().splitlines() if u.strip()]
    print(f"{len(uris)} track URIs from {args.uris}")
    if args.dry_run:
        for u in uris[:10]:
            print("  " + u)
        print(f"  ... ({len(uris)} total) — dry run, nothing sent")
        return 0

    env = R.load_env(ROOT / ".env")
    token = authorise(env["client_id"], env["client_secret"], args.manual)

    me = R.api_get("/me", {}, token)
    print(f"authorised as {me.get('display_name') or me['id']}")

    pl = api_post(
        f"/users/{me['id']}/playlists",
        {"name": args.name, "public": bool(args.public), "description": args.description},
        token,
    )
    print(f"created playlist: {pl['external_urls']['spotify']}")

    for i in range(0, len(uris), BATCH):
        chunk = uris[i:i + BATCH]
        api_post(f"/playlists/{pl['id']}/tracks", {"uris": chunk}, token)
        print(f"  added {i + len(chunk)}/{len(uris)}")

    print("done: " + pl["external_urls"]["spotify"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
