# ultimate-playlist

Every CD on the shelf, transcribed from a photo taken 2026-09-22.

The photo shows three rows of jewel cases seen edge-on, roughly **70–75 discs**.
**41 are identified below** — 33 by artist and album, 8 by artist alone. The
rest are legible only as a coloured spine — the
thin grey and white cases in the top row especially — and are listed as
unreadable rather than guessed at. Books share the shelf and are not included.

## Files

| file | what it is |
|---|---|
| `albums.csv` | the shelf as read from the photo, with a confidence column |
| `albums_spotify.csv` | the same albums resolved to Spotify album IDs |
| `playlist.csv` | every track of every resolved album, with its track URI |
| `playlist_uris.txt` | just the URIs — what an "add to playlist" call wants |
| `resolve_spotify.py` | album → Spotify ID, via the Client Credentials flow |
| `build_playlist.py` | albums → track list |
| `create_playlist.py` | writes the playlist to your account (needs your approval once) |

Credentials live in `.env`, which is gitignored and must stay that way:

```
client_id=...
client_secret=...
```

## Row 1 — top row of cases

| # | Artist | Album |
|---|---|---|
| 1 | Kings of Leon | Only By The Night |
| 2 | Michael Jackson | Number Ones |
| 3 | Justin Timberlake | The 20/20 Experience |

Plus **one further Kings of Leon case** (black spine, title not readable) and
roughly **17 unreadable** cases.

## Row 2 — middle row

| # | Artist | Album |
|---|---|---|
| 4 | Nat King Cole | The Very Best of Nat King Cole |
| 5 | Joshua Radin | We Were Here |
| 6 | Joshua Radin | Underwater |
| 7 | Joshua Radin | Simple Times |
| 8 | Jack Johnson | Sing-A-Longs and Lullabies for the Film Curious George |
| 9 | Bon Jovi | Crush |
| 10 | James Blunt | Moon Landing |
| 11 | Bob Dylan | Highway 61 Revisited |
| 12 | The Doors | *(Elektra release, title not readable)* |
| 13 | Eminem | The Eminem Show |
| 14 | Phil Collins | …Hits |

Plus a **second James Blunt**, a **second Eminem**, a **Beatles** case (pink
spine), a **Run-D.M.C.** case, one case whose only readable mark is the catalogue
number **759P-74007-2**, and roughly **10 unreadable**.

## Row 3 — bottom row

| # | Artist | Album |
|---|---|---|
| 15 | Razorlight | *(self-titled or untitled on the spine)* |
| 16 | Ed Sheeran | + (Plus) |
| 17 | Ed Sheeran | x (Multiply) |
| 18 | Coldplay | Live 2003 |
| 19 | Jack Johnson | Sleep Through the Static |
| 20 | Jack Johnson | On and On |
| 21 | Bob Dylan | The Times They Are A-Changin' |
| 22 | David Bowie | ChangesBowie |
| 23 | Creedence Clearwater Revival | Chronicle |
| 24 | Eagles | Hotel California |
| 25 | Pink Floyd | A Foot in the Door — The Best of Pink Floyd |
| 26 | Simon & Garfunkel | Greatest Hits |
| 27 | The Kooks | *(title not readable)* |
| 28 | De Palmas | Les Lois de la Nature |
| 29 | De Palmas | Marcher dans le sable |
| 30 | Various | Country's Greatest Hits *(box set)* |
| 31 | Various | The Real… Jazz *(3 CD)* |
| 32 | Bob Dylan | The Real… Bob Dylan *(3 CD)* |
| 33 | Alicia Keys | Unplugged |
| 34 | Richard David Precht | Wer bin ich – und wenn ja, wie viele? *(audiobook)* |

Plus roughly **5 unreadable**.

## Counts

| | discs |
|---|---|
| identified by artist and album | 33 |
| identified by artist only | 8 |
| unreadable | ~33 |
| **total on the shelf** | **~74** |

## On Spotify

All 31 album entries were looked up in the catalogue (French market).

| outcome | albums |
|---|---|
| matched | 25 |
| substituted — the exact release is not on Spotify | 4 |
| not on Spotify at all | 2 |
| **expanded into tracks** | **29 albums · 516 tracks · 33h58m** |

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

Two matches are the deluxe edition where the plain one is not on Spotify
(Justin Timberlake, Ed Sheeran's *x*), and Eagles' *Hotel California* resolves
to the 2013 remaster. `Country's Greatest Hits` matched a compilation of the
same name, which may not be the same box set as the disc on the shelf — it is
the one place where a title matched but the release may not.

## Creating the playlist

The scripts above use the Client Credentials flow, which can read the whole
catalogue but cannot touch an account. Writing a playlist needs a user token,
so it takes one approval from you:

1. In the Spotify developer dashboard for this app, add the redirect URI
   `http://127.0.0.1:8888/callback`.
2. Run it, approve in the browser that opens:

```bash
python3 create_playlist.py --name "Ultimate Playlist"
python3 create_playlist.py --dry-run      # see what it would add first
```

Without that, `playlist_uris.txt` can be pasted straight into a Spotify client.

## Finishing the list

The unreadable spines need a closer photo — one per row, taken square-on from
about a metre, is enough. Send those and the list gets completed in place.

## How this was made

The source photo was cropped into three rows and then into twelve overlapping
strips, each enlarged 4×, and read strip by strip. Nothing here is inferred from
a colour or a guess at a partial word: an entry appears only where the spine text
was actually legible, and everything else is counted as unreadable.

`albums.csv` holds the same data for machine use.
