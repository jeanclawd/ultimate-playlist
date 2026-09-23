# ultimate-playlist

A CD shelf, transcribed from a photo taken 2026-09-22, resolved against the
Spotify catalogue, and browsable as a web app.

**[Browse the shelf →](https://jeanclawd.github.io/ultimate-playlist/)**

The photo shows three rows of jewel cases seen edge-on, **70 discs** in all.
**60 albums are identified**, 5 more are known by artist alone, and 5 spines are
still unread. Rows 1 and 2 were dictated by the shelf's owner after the
photograph proved too coarse to read; row 3 and the rest were read from the
image.

Physical occupancy is uneven and worth knowing: row 1 holds 16 discs, row 2
holds 29, row 3 holds 25. The top row stops early to make room for the books
leaning on it.

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
| 27 | Joshua Radin | The Rock and the Tide |
| 28 | Phil Collins | Testify |
| 29 | Queen | Greatest Hits III |
| 30 | Coldplay | Parachutes |
| 31 | De Palmas | Sortir |
| 32 | Jamie Cullum | Catching Tales |
| 33 | Rihanna | Good Girl Gone Bad |
| 34 | Rihanna | Unapologetic |
| 35 | Shawn Mendes | Shawn Mendes |
| 36 | James Blunt | Some Kind of Trouble |
| 37 | James Blunt | All the Lost Souls |
| 38 | Eminem | The Marshall Mathers LP |
| 39 | The xx | Coexist |
| 40 | Journey | Don't Stop Believin': The Best of Journey |
| 41 | Olly Murs | Right Place Right Time |
| 42 | John Denver | The Best of John Denver |

Known only by artist: **The Doors** (Elektra release), **The Beatles**, and
**Run-D.M.C.** — the last of which did not appear in the owner's own list of the
row, so it may have been misread from the photograph.

## Row 3 — bottom row

| # | Artist | Album |
|---|---|---|
| 43 | Ed Sheeran | + (Plus) |
| 44 | Ed Sheeran | x (Multiply) |
| 45 | Coldplay | Live 2003 |
| 46 | Jack Johnson | Sleep Through the Static |
| 47 | Jack Johnson | On and On |
| 48 | Bob Dylan | The Times They Are A-Changin' |
| 49 | David Bowie | ChangesBowie |
| 50 | Creedence Clearwater Revival | Chronicle |
| 51 | Eagles | Hotel California |
| 52 | Pink Floyd | A Foot in the Door — The Best of Pink Floyd |
| 53 | Simon & Garfunkel | Greatest Hits |
| 54 | De Palmas | Les Lois de la Nature |
| 55 | De Palmas | Marcher dans le sable |
| 56 | Various | Country's Greatest Hits |
| 57 | Various | The Real… Jazz |
| 58 | Bob Dylan | The Real… Bob Dylan |
| 59 | Alicia Keys | Unplugged |
| 60 | Richard David Precht | Wer bin ich – und wenn ja, wie viele? |

Known only by artist: **Razorlight**, **The Kooks**. Five more are unreadable —
the only genuine gap left on the shelf.

## On Spotify

| outcome | albums |
|---|---|
| matched | 52 |
| substituted — the exact release is not on Spotify | 6 |
| not on Spotify at all | 2 |
| **expanded into tracks** | **58 albums · 1012 tracks · 65h59m** |

The six substitutions, each checked by hand rather than settled for by the
matcher:

| on the shelf | on Spotify instead | why |
|---|---|---|
| Nat King Cole — The Very Best of Nat King Cole | The Nat King Cole Story | that compilation is absent |
| Phil Collins — …Hits | The Singles | the 1998 compilation is absent |
| David Bowie — ChangesBowie | ChangesOneBowie | only the One/Two/Now editions are there |
| Bob Dylan — The Real… Bob Dylan | The Essential Bob Dylan | the Sony box set is absent |
| Journey — Don't Stop Believin': The Best of Journey | The Essential Journey | that best-of is absent |
| John Denver — The Best of John Denver | The Essential John Denver | no album of that name exists there |

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
dependencies. **Click any cover and it plays**, in a dock at the bottom of the
page; the ▶ beside a track plays that track. Playback goes through Spotify's
embed, so it needs no login: a visitor hears 30-second previews, and anyone
already signed in to Premium hears whole tracks. The page drives it with
Spotify's iFrame API so one click starts the music, and falls back to a plain
embed if that script is unavailable.

It also lets you search across artists, albums and track titles, sort by artist
or year, and pick whole albums or individual tracks. Then:

- **Open** on any card opens that CD on Spotify, and the ↗ beside any track
  opens that track;
- **Open in Spotify** opens the selection — the album when a whole album is
  selected and nothing else, otherwise the first selected track;
- **Create playlist** builds the whole selection on your Spotify account.

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

Pages is live, served from `main` / `/docs`. Note that on a free plan the
repository has to be public for Pages to serve at all — a private repo returns
422 from the Pages API.

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

Five spines in row 3 are still unread, and three cases in row 2 give an artist
but no title (The Doors, The Beatles, Run-D.M.C.). A closer photo of the
right-hand end of row 3 would finish the shelf.

## How this was made

The photo was cropped into three rows and then into twelve overlapping strips,
each enlarged 4×, and read strip by strip. Nothing is inferred from a colour or
a half-word: an entry appears only where the spine text was legible, where the
owner supplied it, or where it is marked unreadable.
