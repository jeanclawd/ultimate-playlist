# ultimate-playlist

A CD shelf, transcribed from a photo taken 2026-09-22, resolved against the
Spotify catalogue, and browsable as a web app.

**[Browse the shelf →](https://jeanclawd.github.io/ultimate-playlist/)**
(once GitHub Pages is switched on — see *Serving the app* below)

The photo shows three rows of jewel cases seen edge-on. **44 albums are
identified**, 7 more are known by artist alone, and roughly 16 spines are still
unread. The top row was supplied by the shelf's owner after the photo proved too
low-resolution to read; everything else was read from the image.

## Files

| file | what it is |
|---|---|
| `albums.csv` | the shelf as read, with a confidence column |
| `albums_spotify.csv` | the same albums resolved to Spotify album IDs |
| `playlist.csv` | every track of every resolved album, with its track URI |
| `playlist_uris.txt` | just the URIs — what an "add to playlist" call wants |
| `docs/` | the browser app served by GitHub Pages |
| `resolve_spotify.py` | album → Spotify ID, via the Client Credentials flow |
| `build_playlist.py` | albums → track list |
| `build_site_data.py` | builds `docs/data.json`, including cover art |
| `create_playlist.py` | writes the playlist to an account from the command line |

Credentials live in `.env`, which is gitignored and must stay that way:

```
client_id=...
client_secret=...
```

`.env` has never been committed — verified against the full object history.

## Row 1 — top row

| # | Artist | Album |
|---|---|---|
| 1 | Kings of Leon | Only By The Night |
| 2 | Michael Jackson | Number Ones |
| 3 | Justin Timberlake | The 20/20 Experience |
| 4 | Kaiser Chiefs | Yours Truly, Angry Mob |
| 5 | Bruno Mars | Doo-Wops & Hooligans |
| 6 | Kings of Leon | Youth and Young Manhood |
| 7 | Selena Gomez | Revival |
| 8 | Queen | Greatest Hits II |
| 9 | fun. | Some Nights |
| 10 | Florence + The Machine | Ceremonials |
| 11 | Snow Patrol | Up to Now |
| 12 | Kanye West | Late Registration |
| 13 | Maroon 5 | It Won't Be Soon Before Long |
| 14 | Maroon 5 | Songs About Jane |
| 15 | Maroon 5 | Red Pill Blues |
| 16 | Maroon 5 | Overexposed |

## Row 2 — middle row

| # | Artist | Album |
|---|---|---|
| 17 | Nat King Cole | The Very Best of Nat King Cole |
| 18 | Joshua Radin | We Were Here |
| 19 | Joshua Radin | Underwater |
| 20 | Joshua Radin | Simple Times |
| 21 | Jack Johnson | Sing-A-Longs and Lullabies for the Film Curious George |
| 22 | Bon Jovi | Crush |
| 23 | James Blunt | Moon Landing |
| 24 | Bob Dylan | Highway 61 Revisited |
| 25 | Eminem | The Eminem Show |
| 26 | Phil Collins | …Hits |

Known only by artist: **The Doors** (Elektra release), a second **James Blunt**,
a second **Eminem**, **The Beatles**, **Run-D.M.C.** One case shows only the
catalogue number `759P-74007-2`, and about 10 more are unreadable.

## Row 3 — bottom row

| # | Artist | Album |
|---|---|---|
| 27 | Ed Sheeran | + (Plus) |
| 28 | Ed Sheeran | x (Multiply) |
| 29 | Coldplay | Live 2003 |
| 30 | Jack Johnson | Sleep Through the Static |
| 31 | Jack Johnson | On and On |
| 32 | Bob Dylan | The Times They Are A-Changin' |
| 33 | David Bowie | ChangesBowie |
| 34 | Creedence Clearwater Revival | Chronicle |
| 35 | Eagles | Hotel California |
| 36 | Pink Floyd | A Foot in the Door — The Best of Pink Floyd |
| 37 | Simon & Garfunkel | Greatest Hits |
| 38 | De Palmas | Les Lois de la Nature |
| 39 | De Palmas | Marcher dans le sable |
| 40 | Various | Country's Greatest Hits |
| 41 | Various | The Real… Jazz |
| 42 | Bob Dylan | The Real… Bob Dylan |
| 43 | Alicia Keys | Unplugged |
| 44 | Richard David Precht | Wer bin ich – und wenn ja, wie viele? |

Known only by artist: **Razorlight**, **The Kooks**. About 5 more are unreadable.

## On Spotify

| outcome | albums |
|---|---|
| matched | 38 |
| substituted — the exact release is not on Spotify | 4 |
| not on Spotify at all | 2 |
| **expanded into tracks** | **42 albums · 737 tracks · 48h06m** |

The four substitutions, each checked by hand rather than settled for by the
matcher:

| on the shelf | on Spotify instead | why |
|---|---|---|
| Nat King Cole — The Very Best of Nat King Cole | The Nat King Cole Story | that compilation is absent |
| Phil Collins — …Hits | The Singles | the 1998 compilation is absent |
| David Bowie — ChangesBowie | ChangesOneBowie | only the One/Two/Now editions are there |
| Bob Dylan — The Real… Bob Dylan | The Essential Bob Dylan | the Sony box set is absent |

Not available in any form: **The Real… Jazz** (same Sony series) and the
**Precht audiobook**, which is not in the music catalogue.

Several matches are a deluxe edition where the plain one is not in the
catalogue, and Eagles' *Hotel California* resolves to the 2013 remaster.
`Country's Greatest Hits` matched a compilation of the same name, which may not
be the same box set as the disc on the shelf — the one place where a title
matched but the release may not.

### Matching is deliberately suspicious

A naive title match got several albums wrong: a tribute act called *Eagles
Experience* outscored the real Eagles, and Ed Sheeran's *+* matched his 2025
album *Play*. So `resolve_spotify.py` penalises artist names that add words to
the one being searched for, strips edition noise before comparing titles,
discards one-track "albums", and keeps an explicit list of releases verified
absent from the catalogue rather than accepting a near-miss for them.

## The app

`docs/index.html` is a single self-contained page — no build step, no
dependencies. It lets you browse the shelf by row, search across artists,
albums and track titles, pick whole albums or individual tracks, and then

- copy the selected track URIs,
- download them as a text file, or
- create the playlist directly on your Spotify account.

That last one uses the PKCE flow, so it needs only a **client ID** — no secret
is involved and nothing is stored anywhere but your own browser. Add the page's
own URL as a redirect URI in your Spotify app first; the page shows you the
exact string to paste.

Regenerate the data after changing the shelf:

```bash
python3 resolve_spotify.py     # albums  -> Spotify IDs
python3 build_playlist.py      # albums  -> tracks
python3 build_site_data.py     # both    -> docs/data.json, with cover art
```

## Serving the app

GitHub Pages needs to be switched on once, in **Settings → Pages**: source
`Deploy from a branch`, branch `main`, folder `/docs`. On a free plan the
repository must be public for Pages to serve.

Locally, no setup required:

```bash
cd docs && python3 -m http.server 8000
```

## Creating the playlist from the command line

An alternative to the app, same result:

1. Add `http://127.0.0.1:8888/callback` as a redirect URI in the Spotify app.
2. Run it:

```bash
python3 create_playlist.py --name "Ultimate Playlist"
python3 create_playlist.py --dry-run      # see what it would add first
```

## Finishing the list

The ~16 unread spines need a closer photo — one per row, square-on, from about
a metre. Send those and the list gets completed in place.

## How this was made

The photo was cropped into three rows and then into twelve overlapping strips,
each enlarged 4×, and read strip by strip. Nothing is inferred from a colour or
a half-word: an entry appears only where the spine text was legible, where the
owner supplied it, or where it is marked unreadable.
