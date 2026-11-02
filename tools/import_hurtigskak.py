#!/usr/bin/env python3
"""
Læser Jens' regneark med hurtigskak-stillingen og skriver data/hurtigskak.json.

Brug:
    python3 -P tools/import_hurtigskak.py ~/Downloads/Hurtigskak-resultater.xlsx
    python3 build.py && ./deploy.sh

ARKETS OPBYGNING
Hver spiller fylder to rækker, og resultaterne står i rækken OVER navnet:

    r5                                        (Allans resultater - tom)
    r6   1  Allan   <modstandernes numre>
    r7           1  ½  1  1  0  ½      8      (Bents resultater og total)
    r8   2  Bent    4  3  7  6 11  3          (Bents modstandere)

Den rækkefølge er ikke til at gætte, så scriptet kontrollerer den: i et
korrekt skema skal de to spilleres resultater i samme parti passe sammen
(1 mod 0, ½ mod ½). Passer de ikke, er rækkerne forskudt, og scriptet
stopper i stedet for at udgive en forkert stilling.

Runderne står i kolonne C-K (3 aftener à 3 runder), totalen i kolonne L.
Totalen regnes efter 2/1/0, så et resultat på "1" giver 2 point.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import openpyxl
except ModuleNotFoundError:
    sys.exit("openpyxl mangler:  pip install openpyxl")

# data/ hører til repoet og følger med ved udrulning. content/ hører til
# serveren, fordi administratorerne redigerer det via /admin - en fil der
# laves ud fra Jens' regneark, skal derfor IKKE ligge der.
OUT = Path(__file__).resolve().parent.parent / "data" / "hurtigskak.json"

FIRST_NAME_ROW = 6
FIRST_ROUND_COL = 3                      # kolonne C
N_ROUNDS = 9
TOTAL_COL = 12                           # kolonne L
SEASON_EVENINGS = 6                      # 3 aftener i efteråret + 3 i foråret
RESULT_ROW_OFFSET = -1                   # resultaterne står OVER navnet
POINTS = {"1": 2, "½": 1, "0": 0}        # gevinst / remis / tab i de lange partier
COMPLEMENT = {"1": "0", "0": "1", "½": "½"}


def cell(ws, r, c) -> str:
    v = ws.cell(r, c).value
    if v is None:
        return ""
    if isinstance(v, float) and v == int(v):
        v = int(v)
    return str(v).strip().replace("0.5", "½")


def read_players(ws) -> list[dict]:
    players = []
    for r in range(FIRST_NAME_ROW, ws.max_row + 1, 2):
        name = cell(ws, r, 2)
        if not name:
            continue
        rr = r + RESULT_ROW_OFFSET
        players.append({
            "no": cell(ws, r, 1),
            "name": name,
            "opponents": [cell(ws, r, FIRST_ROUND_COL + i) for i in range(N_ROUNDS)],
            "results": [cell(ws, rr, FIRST_ROUND_COL + i) for i in range(N_ROUNDS)],
            "total": cell(ws, rr, TOTAL_COL),
        })
    return players


def check_pairings(players: list[dict]) -> tuple[int, list[str]]:
    """De to spilleres resultater i samme parti skal passe sammen.

    Det er den kontrol, der afslører, om navne- og resultatrækker er
    forskudt i forhold til hinanden. Returnerer (antal kontrollerede
    partier, liste over modstrid).
    """
    by_no = {p["no"]: p for p in players}
    checked, problems = 0, []
    for p in players:
        for i in range(N_ROUNDS):
            opp, res = p["opponents"][i], p["results"][i]
            other = by_no.get(opp)
            if not (opp and res and other and other["results"][i]):
                continue
            checked += 1
            theirs = other["results"][i]
            if COMPLEMENT.get(res) != theirs:
                problems.append(
                    f"runde {i + 1}: {p['name']} har {res} mod {other['name']}, "
                    f"men {other['name']} har {theirs}")
    return checked // 2, problems


def main(path: str) -> None:
    ws = openpyxl.load_workbook(path, data_only=True).worksheets[0]
    players = read_players(ws)

    games, problems = check_pairings(players)
    if problems:
        print(f"✗ {len(problems)} partier hænger ikke sammen. Enten er navne- og\n"
              f"  resultatrækker forskudt (se RESULT_ROW_OFFSET), eller også er der\n"
              f"  en tastefejl i arket. Der er ikke skrevet noget.\n")
        for p in problems[:10]:
            print(f"   - {p}")
        sys.exit(1)

    # Aftenernes datoer står i række 3 over hver sin gruppe på tre runder.
    evenings = []
    for i in range(3):
        raw = ws.cell(3, FIRST_ROUND_COL + i * 3).value
        evenings.append({
            "no": i + 1,
            "date": raw.strftime("%Y-%m-%d") if hasattr(raw, "strftime") else "",
            "rounds": [i * 3 + 1, i * 3 + 2, i * 3 + 3],
        })

    notes = []
    for p in players:
        computed = sum(POINTS.get(x, 0) for x in p["results"])
        if p["total"] and str(computed) != p["total"]:
            notes.append(f"{p['name']}: arket siger {p['total']}, "
                         f"resultaterne giver {computed}")
        missing = [i + 1 for i, (o, x) in enumerate(zip(p["opponents"], p["results"]))
                   if o and not x]
        if missing:
            notes.append(f"{p['name']}: modstander uden resultat i runde "
                         + ",".join(map(str, missing)))

    played_rounds = max((i + 1 for p in players
                         for i, x in enumerate(p["results"]) if x), default=0)
    evenings_played = -(-played_rounds // 3)        # rund op til hele aftener

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "heading": f"Stilling efter runde {evenings_played} af {SEASON_EVENINGS}",
        "evenings": evenings,
        "players": players,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"✓ {OUT.name}: {len(players)} spillere, {played_rounds} runder "
          f"({evenings_played} aftener)")
    print(f"  {games} partier kontrolleret - alle hænger sammen")
    print("  " + " · ".join(f"{p['name']} {p['total'] or '–'}" for p in players))
    if notes:
        print(f"\n⚠ {len(notes)} ting at kigge efter i arket:")
        for n in notes:
            print(f"   - {n}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
