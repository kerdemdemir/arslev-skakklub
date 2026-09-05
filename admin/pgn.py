#!/usr/bin/env python3
"""
Indlæsning af PGN-filer til partiarkivet.

Al skak-logik foregår her på serveren med python-chess. Browseren får en
færdig liste af stillinger (FEN) og træk, så viseren ikke selv skal kunne
skakreglerne - den skal bare tegne et bræt.

Partierne gemmes som:
  content/games/index.json   liste med oplysninger om hvert parti
  content/games/<id>.json    ét parti med træk og den oprindelige PGN
"""
from __future__ import annotations

import io
import json
import re
import secrets
import unicodedata
from datetime import date
from pathlib import Path

import chess
import chess.pgn

MAX_PGN_BYTES = 4 * 1024 * 1024      # 4 MB PGN-tekst
MAX_GAMES_PER_IMPORT = 200
MAX_PLIES = 600                       # sikkerhedsventil mod absurd lange partier

HEADERS = ("Event", "Site", "Date", "Round", "White", "Black",
           "Result", "ECO", "WhiteElo", "BlackElo", "TimeControl")


def _slug(s: str) -> str:
    s = (s or "").lower()
    for a, b in (("æ", "ae"), ("ø", "oe"), ("å", "aa")):
        s = s.replace(a, b)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s)).strip("-")[:40]


def _clean_date(raw: str) -> str:
    """PGN-datoer kan være ukendte ("????.??.??") eller kun have et årstal.
    Vi returnerer det, der faktisk er oplyst - og ellers en tom streng."""
    parts = (raw or "").replace("-", ".").split(".")
    year = parts[0] if parts and parts[0].isdigit() and len(parts[0]) == 4 else ""
    if not year:
        return ""
    out = year
    for p in parts[1:3]:
        if not p.isdigit():
            break
        out += f"-{int(p):02d}"
    return out


class GameStore:
    def __init__(self, root: Path):
        self.dir = root / "content" / "games"
        self.index_file = self.dir / "index.json"

    # ------------------------------------------------------------------ læs
    def index(self) -> list[dict]:
        if not self.index_file.exists():
            return []
        games = json.loads(self.index_file.read_text(encoding="utf-8")).get("games", [])
        games.sort(key=lambda g: (g.get("date") or "", g.get("added") or ""), reverse=True)
        return games

    def get(self, game_id: str) -> dict | None:
        if not re.fullmatch(r"[a-z0-9-]{1,80}", game_id or ""):
            return None
        f = self.dir / f"{game_id}.json"
        if not f.is_file() or f.resolve().parent != self.dir.resolve():
            return None
        return json.loads(f.read_text(encoding="utf-8"))

    # ----------------------------------------------------------------- skriv
    def _write_index(self, games: list[dict]) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        tmp = self.index_file.with_suffix(".json.tmp")
        tmp.write_text(json.dumps({"games": games}, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
        tmp.replace(self.index_file)

    def delete(self, game_id: str) -> bool:
        game = self.get(game_id)
        if not game:
            return False
        (self.dir / f"{game_id}.json").unlink(missing_ok=True)
        self._write_index([g for g in self.index() if g["id"] != game_id])
        return True

    def add_from_pgn(self, text: str, added_by: str = "admin") -> tuple[int, list[str]]:
        """Læser alle partier i en PGN-tekst. Returnerer (antal, advarsler).

        added_by er den rolle, der importerede partiet. Et medlem må slette
        sine egne importer igen, men ikke dem administratoren har lagt ind.
        """
        if len(text.encode("utf-8", "ignore")) > MAX_PGN_BYTES:
            raise ValueError("PGN-filen er for stor (højst 4 MB).")

        stream = io.StringIO(text)
        index = self.index()
        taken = {g["id"] for g in index}
        added, warnings = 0, []

        while added < MAX_GAMES_PER_IMPORT:
            try:
                game = chess.pgn.read_game(stream)
            except Exception as e:                                  # noqa: BLE001
                warnings.append(f"Kunne ikke læse et parti: {e}")
                break
            if game is None:
                break

            parsed, warn = self._parse_game(game)
            warnings.extend(warn)
            if parsed is None:
                continue

            base = "-".join(x for x in (
                (parsed["date"] or "").replace(".", "-")[:10],
                _slug(parsed["white"]), "vs", _slug(parsed["black"])) if x) or "parti"
            gid = base
            while gid in taken:
                gid = f"{base}-{secrets.token_hex(2)}"
            taken.add(gid)

            parsed["id"] = gid
            parsed["added"] = date.today().isoformat()
            parsed["added_by"] = added_by

            self.dir.mkdir(parents=True, exist_ok=True)
            (self.dir / f"{gid}.json").write_text(
                json.dumps(parsed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            index.append({k: parsed[k] for k in
                          ("id", "added", "added_by", "event", "site", "date", "round",
                           "white", "black", "result", "eco", "plies")})
            added += 1

        if added:
            self._write_index(index)
        return added, warnings

    # ------------------------------------------------------------ enkelt parti
    @staticmethod
    def _parse_game(game: chess.pgn.Game) -> tuple[dict | None, list[str]]:
        warn: list[str] = []
        h = game.headers
        white = h.get("White", "?") or "?"
        black = h.get("Black", "?") or "?"

        board = game.board()
        start_fen = board.fen()
        moves = []
        for node in game.mainline():
            if len(moves) >= MAX_PLIES:
                warn.append(f"{white}–{black}: partiet blev afkortet ved {MAX_PLIES} halvtræk.")
                break
            mv = node.move
            if mv is None:
                continue
            try:
                san = board.san(mv)
            except Exception:                                       # noqa: BLE001
                warn.append(f"{white}–{black}: et ulovligt træk blev sprunget over.")
                break
            board.push(mv)
            moves.append({
                "ply": len(moves) + 1,
                "san": san,
                "uci": mv.uci(),
                "from": chess.square_name(mv.from_square),
                "to": chess.square_name(mv.to_square),
                "fen": board.fen(),
                "comment": (node.comment or "").strip()[:400],
            })

        if not moves:
            warn.append(f"{white}–{black}: partiet indeholdt ingen træk og blev ikke gemt.")
            return None, warn

        return {
            "event": h.get("Event", "") or "",
            "site": h.get("Site", "") or "",
            "date": _clean_date(h.get("Date", "")),
            "round": h.get("Round", "") or "",
            "white": white,
            "black": black,
            "result": h.get("Result", "*") or "*",
            "eco": h.get("ECO", "") or "",
            "white_elo": h.get("WhiteElo", "") or "",
            "black_elo": h.get("BlackElo", "") or "",
            "start_fen": start_fen,
            "plies": len(moves),
            "moves": moves,
            "pgn": str(game),
        }, warn
