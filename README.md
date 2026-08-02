# BitTorrent Client

A BitTorrent client written from scratch in Python — no third-party BitTorrent or bencode libraries. It parses `.torrent` files, announces to HTTP trackers, performs the peer wire protocol handshake, and downloads and verifies real file data from peers on the live BitTorrent network.

This project started from [CodeCrafters'](https://codecrafters.io) "Build Your Own BitTorrent" challenge and was substantially refactored afterward: the original single-file, copy-pasted implementation was split into focused modules, a from-scratch bencode encoder was added (the original relied on a third-party library for encoding), and the CLI was rebuilt on `argparse` instead of manual `sys.argv` parsing.

## What it does

- Decodes and encodes [bencode](https://wiki.theory.org/BitTorrentSpecification#Bencoding), BitTorrent's serialization format, entirely from scratch
- Parses `.torrent` files and computes the info hash
- Announces to an HTTP tracker and retrieves a peer list
- Performs the BitTorrent peer handshake and message exchange (bitfield, interested, unchoke)
- Downloads individual pieces or entire files from a real peer, verifying each piece's SHA1 hash against the `.torrent` file's metadata before accepting it

## Architecture

| Module | Responsibility |
|---|---|
| `bencode.py` | Bencode decoding and encoding — no dependencies |
| `torrent.py` | `Torrent` class: parses a `.torrent` file into a reusable object (announce URL, length, piece length, piece hashes, info hash) |
| `tracker.py` | Announces to the tracker over HTTP and parses the compact peer list |
| `peer.py` | The peer wire protocol — handshake, unchoke sequence, and block-level piece requests with hash verification |
| `cli.py` | Command-line entry point, built on `argparse` |

Each module only depends on the one(s) below it in this table, so each can be tested in isolation.

## Setup

Requires Python 3.14+ and the `requests` library.

```bash
pip install requests
```

(or `uv sync`, if using the included `uv.lock`)

## Usage

Run all commands from the repository root.

**Decode a raw bencoded value:**
```bash
python3 app/cli.py decode "d3:foo3:bare"
```

**Show a torrent's metadata:**
```bash
python3 app/cli.py info sample.torrent
```

**List peers from the tracker:**
```bash
python3 app/cli.py peers sample.torrent
```

**Download a single piece:**
```bash
python3 app/cli.py download_piece -o piece0.bin sample.torrent 0
```

**Download the full file:**
```bash
python3 app/cli.py download -o output.bin sample.torrent
```

## Known limitations

This is a functional client, not a production-grade one. Notable gaps, roughly in order of impact:

- **Single peer per download** — no concurrent multi-peer downloading, so speed is limited to one connection, and there's no failover if that peer drops
- **No request pipelining** — blocks are requested one at a time, waiting for each response before sending the next
- **Single-file torrents only** — multi-file torrents (`info.files`) aren't supported
- **HTTP trackers only** — no UDP tracker support, and no fallback across an `announce-list`
- **No magnet link support** — `.torrent` files only
- **Download only** — the client doesn't seed/upload pieces to other peers

## Possible next steps

- Concurrent downloading across multiple peers, with pipelined block requests
- Peer retry/failover
- Multi-file torrent support
- UDP tracker support
- Rarest-first piece selection
- Magnet link support (BEP 9 metadata exchange)
