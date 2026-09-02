#!/usr/bin/env python3
"""
Genererer et statisk kortbillede over spillestedet ud fra OpenStreetMaps
raster-fliser, så siden ikke behøver en indlejret kortwidget (som kræver WebGL).

Kør kun når kortet skal opdateres:   python3 tools/make_map.py
Resultatet gemmes i assets/img/kort.png og committes til repoet.
"""
import io
import math
import pathlib
import time
import urllib.request

LAT, LON = 55.30767, 10.48484      # Over Bækken, 5792 Årslev
ZOOM = 16
WIDTH, HEIGHT = 1000, 750
TILE = 256
UA = "arslevskak-website/1.0 (statisk kortgenerering; https://aarslevskak.com)"
OUT = pathlib.Path("assets/img/kort.png")

from PIL import Image, ImageDraw, ImageFont


def deg2px(lat, lon, z):
    n = 2 ** z * TILE
    x = (lon + 180.0) / 360.0 * n
    s = math.sin(math.radians(lat))
    y = (0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n
    return x, y


def fetch(z, x, y):
    url = f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return Image.open(io.BytesIO(r.read())).convert("RGB")


def main():
    cx, cy = deg2px(LAT, LON, ZOOM)
    left, top = cx - WIDTH / 2, cy - HEIGHT / 2
    tx0, ty0 = int(left // TILE), int(top // TILE)
    tx1, ty1 = int((left + WIDTH) // TILE), int((top + HEIGHT) // TILE)

    canvas = Image.new("RGB", ((tx1 - tx0 + 1) * TILE, (ty1 - ty0 + 1) * TILE), "#e8e0d8")
    for tx in range(tx0, tx1 + 1):
        for ty in range(ty0, ty1 + 1):
            try:
                canvas.paste(fetch(ZOOM, tx, ty), ((tx - tx0) * TILE, (ty - ty0) * TILE))
            except Exception as e:            # en manglende flise må ikke vælte bygget
                print(f"  ! flise {ZOOM}/{tx}/{ty}: {e}")
            time.sleep(0.12)                  # vær pæn ved OSMs fliseserver

    img = canvas.crop((int(left - tx0 * TILE), int(top - ty0 * TILE),
                       int(left - tx0 * TILE) + WIDTH, int(top - ty0 * TILE) + HEIGHT))

    d = ImageDraw.Draw(img, "RGBA")
    mx, my = WIDTH // 2, HEIGHT // 2
    # nål i klubbens guld/sort
    d.polygon([(mx - 13, my - 8), (mx + 13, my - 8), (mx, my + 20)], fill=(20, 17, 13, 255))
    d.ellipse([mx - 21, my - 42, mx + 21, my], fill=(20, 17, 13, 255))
    d.ellipse([mx - 17, my - 38, mx + 17, my - 4], fill=(216, 169, 78, 255))
    d.ellipse([mx - 7, my - 28, mx + 7, my - 14], fill=(20, 17, 13, 255))

    # attribution bages ind i billedet (krav ved brug af OSM-data)
    txt = "© OpenStreetMap contributors"
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    except OSError:
        font = ImageFont.load_default()
    tw = d.textlength(txt, font=font)
    d.rectangle([WIDTH - tw - 16, HEIGHT - 24, WIDTH, HEIGHT], fill=(255, 255, 255, 200))
    d.text((WIDTH - tw - 8, HEIGHT - 20), txt, fill=(60, 55, 48, 255), font=font)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    # kortfliser har få farver, så en paletbaseret PNG er både skarp og lille
    img.quantize(colors=128, method=Image.MAXCOVERAGE).save(OUT, optimize=True)
    print(f"  → {OUT} ({OUT.stat().st_size // 1024} kB, {WIDTH}×{HEIGHT}, zoom {ZOOM})")


if __name__ == "__main__":
    main()
