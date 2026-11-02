#!/usr/bin/env python3
"""
Læser Jens' regneark med hurtigskak-stillingen og skriver content/hurtigskak.json.

Brug:
    python3 -P tools/import_hurtigskak.py ~/Downloads/Hurtigskak-resultater.xlsx
    python3 build.py && ./deploy.sh

Arket er bygget med to rækker pr. spiller: den første har nummer, navn og
modstandernes numre, den anden har resultaterne og totalen. Runderne står i
kolonne C-K (3 aftener à 3 runder), totalen i kolonne L.

Totalen regnes i arket efter 2/1/0 for de lange partier, så et resultat på
"1" giver 2 point. Scriptet kontrollerer det og siger til, hvis en total
ikke passer - så er der nok en tastefejl i arket.
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
FIRST_ROUND_COL = 3                      # kolonne C
N_ROUNDS = 9
TOTAL_COL = 12                           # kolonne L
SEASON_EVENINGS = 6                      # 3 aftener i efteråret + 3 i foråret
POINTS = {"1": 2, "½": 1, "0": 0}        # gevinst / remis / tab i de lange partier


def cell(ws, r, c) -> str:
    v = ws.cell(r, c).value
    if v is None:
        return ""
    if isinstance(v, float) and v == int(v):
        v = int(v)
    return str(v).strip().replace("0.5", "½")


def main(path: str) -> None:
    ws = openpyxl.load_workbook(path, data_only=True).worksheets[0]

    # Aftenernes datoer står i række 3 over hver sin gruppe på tre runder.
    evenings = []
    for i in range(3):
        raw = ws.cell(3, FIRST_ROUND_COL + i * 3).value
        evenings.append({
            "no": i + 1,
            "date": raw.strftime("%Y-%m-%d") if hasattr(raw, "strftime") else "",
            "rounds": [i * 3 + 1, i * 3 + 2, i * 3 + 3],
        })

    players, warnings = [], []
    r = 6
    while r <= ws.max_row:
        no, name = cell(ws, r, 1), cell(ws, r, 2)
        if not name:
            r += 1
            continue
        opponents = [cell(ws, r, FIRST_ROUND_COL + i) for i in range(N_ROUNDS)]
        results = [cell(ws, r + 1, FIRST_ROUND_COL + i) for i in range(N_ROUNDS)]
        total = cell(ws, r + 1, TOTAL_COL)

        computed = sum(POINTS.get(x, 0) for x in results)
        if total and str(computed) != total:
            warnings.append(f"{name}: arket siger {total}, resultaterne giver {computed}")
        if not total and any(opponents):
            warnings.append(f"{name}: har modstandere, men ingen total")
        # Saml afvigelserne pr. spiller i stedet for pr. runde - ellers
        # drukner den egentlige besked i 37 linjer.
        res_no_opp = [i for i, (o, x) in enumerate(zip(opponents, results), 1) if x and not o]
        opp_no_res = [i for i, (o, x) in enumerate(zip(opponents, results), 1)
                      if o and not x and i <= 6]
        if res_no_opp:
            warnings.append(f"{name}: resultat uden modstander i runde "
                            + ",".join(map(str, res_no_opp)))
        if opp_no_res:
            warnings.append(f"{name}: modstander uden resultat i runde "
                            + ",".join(map(str, opp_no_res)))

        players.append({"no": no, "name": name, "opponents": opponents,
                        "results": results, "total": total})
        r += 2

    # Jens skriver "Stilling efter runde 2 af 6" og tæller AFTENER, ikke
    # enkeltrunder: sæsonen har 6 aftener (3 i efteråret, 3 i foråret).
    played_rounds = max((i + 1 for p in players for i, x in enumerate(p["results"]) if x),
                        default=0)
    evenings_played = -(-played_rounds // 3)        # rund op til hele aftener
    data = {
        "heading": f"Stilling efter runde {evenings_played} af {SEASON_EVENINGS}",
        "evenings": evenings,
        "players": players,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"✓ {OUT.relative_to(Path.cwd())}: {len(players)} spillere, "
          f"{played_rounds} spillede runder ({evenings_played} aftener)")
    if warnings:
        print(f"\n⚠ {len(warnings)} ting at kigge efter i arket:")
        for w in warnings:
            print(f"   - {w}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
