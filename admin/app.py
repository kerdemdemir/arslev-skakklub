#!/usr/bin/env python3
"""
Admin-side for Årslev Skakklub.

Redigerer content/news.json og billederne i assets/img/nyheder/, og kører
derefter build.py + publish.sh, så den statiske side opdateres med det samme.

Den offentlige side forbliver rene statiske filer, som nginx udleverer.
Denne app rører kun ved noget, når en administrator er logget ind, og den
lytter kun på localhost - nginx står for HTTPS og videresender /admin hertil.

Konfiguration læses fra miljøet (se /etc/arslevskak/admin.env på serveren):
  ARSLEV_ADMIN_USER   brugernavn            (default: admin)
  ARSLEV_ADMIN_HASH   bcrypt-hash af koden  (påkrævet)
  ARSLEV_SECRET       nøgle til at signere session-cookien (påkrævet)
  ARSLEV_SITE_DIR     mappen med build.py   (default: /srv/arslevskak)
"""
from __future__ import annotations

import json
import os
import re
import secrets
import subprocess
import threading
import time
import unicodedata
from datetime import date, datetime
from pathlib import Path

import bcrypt
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from PIL import Image, UnidentifiedImageError
# request.form() giver Starlettes UploadFile, ikke FastAPIs underklasse - så det
# er den type, isinstance-tjekket i save() skal bruge.
from starlette.datastructures import UploadFile as FormUpload

# ----------------------------------------------------------------- opsætning
HERE = Path(__file__).resolve().parent
SITE_DIR = Path(os.environ.get("ARSLEV_SITE_DIR", "/srv/arslevskak"))
NEWS_FILE = SITE_DIR / "content" / "news.json"
IMG_DIR = SITE_DIR / "assets" / "img" / "nyheder"
IMG_REL = "nyheder"                       # sti som den står i news.json

ADMIN_USER = os.environ.get("ARSLEV_ADMIN_USER", "admin")
ADMIN_HASH = os.environ.get("ARSLEV_ADMIN_HASH", "").encode()
SECRET = os.environ.get("ARSLEV_SECRET", "")
if not ADMIN_HASH or not SECRET:
    raise SystemExit("ARSLEV_ADMIN_HASH og ARSLEV_SECRET skal være sat")

COOKIE = "arslev_admin"
SESSION_MAX_AGE = 7 * 24 * 3600           # en uge
MAX_UPLOAD = 12 * 1024 * 1024             # 12 MB pr. billede
MAX_EDGE = 2000                           # billeder skaleres ned til dette
IMAGE_SLOTS = 3                           # antal billed-felter i formularen
LOGIN_MAX_TRIES = 5                       # forsøg pr. IP
LOGIN_WINDOW = 15 * 60                    # inden for 15 minutter

signer = URLSafeTimedSerializer(SECRET, salt="arslev-admin-session")
build_lock = threading.Lock()
_attempts: dict[str, list[float]] = {}

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/admin/static", StaticFiles(directory=HERE / "static"), name="static")
tpl = Jinja2Templates(directory=str(HERE / "templates"))


# ------------------------------------------------------------------ hjælpere
def slugify(s: str) -> str:
    s = s.lower()
    for a, b in (("æ", "ae"), ("ø", "oe"), ("å", "aa")):
        s = s.replace(a, b)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s)).strip("-")[:60] or "nyhed"


def load_posts() -> list[dict]:
    if not NEWS_FILE.exists():
        return []
    posts = json.loads(NEWS_FILE.read_text(encoding="utf-8")).get("posts", [])
    posts.sort(key=lambda p: p.get("date", ""), reverse=True)
    return posts


def save_posts(posts: list[dict]) -> None:
    posts.sort(key=lambda p: p.get("date", ""), reverse=True)
    NEWS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = NEWS_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps({"posts": posts}, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    tmp.replace(NEWS_FILE)                # atomisk, så filen aldrig er halv


def publish() -> tuple[bool, str]:
    """Byg siden og kopier den til webroden. Én ad gangen."""
    with build_lock:
        try:
            r = subprocess.run([str(SITE_DIR / "publish.sh")], cwd=SITE_DIR,
                               capture_output=True, text=True, timeout=120)
            return r.returncode == 0, (r.stdout + r.stderr)[-1500:]
        except Exception as e:                                  # noqa: BLE001
            return False, f"{type(e).__name__}: {e}"


# ------------------------------------------------------------------ sessioner
def current_user(request: Request) -> str | None:
    raw = request.cookies.get(COOKIE)
    if not raw:
        return None
    try:
        data = signer.loads(raw, max_age=SESSION_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None
    return data.get("u") if isinstance(data, dict) else None


def require_user(request: Request) -> str:
    u = current_user(request)
    if not u:
        raise HTTPException(status_code=303, headers={"Location": "/admin/login"})
    return u


def csrf_of(request: Request) -> str:
    """CSRF-token udledes af sessionen, så den ikke skal gemmes serverside."""
    raw = request.cookies.get(COOKIE, "")
    import hashlib
    return hashlib.blake2s((SECRET + raw).encode(), digest_size=16).hexdigest()


def check_csrf(request: Request, token: str) -> None:
    if not secrets.compare_digest(token or "", csrf_of(request)):
        raise HTTPException(status_code=400, detail="Ugyldig formular (CSRF). Prøv igen.")


@app.exception_handler(HTTPException)
async def redirect_handler(request: Request, exc: HTTPException):
    if exc.status_code == 303 and "Location" in (exc.headers or {}):
        return RedirectResponse(exc.headers["Location"], status_code=303)
    return HTMLResponse(
        f"<p style='font:16px/1.6 system-ui;padding:40px'>{exc.detail}<br><br>"
        f"<a href='/admin'>Tilbage</a></p>", status_code=exc.status_code)


# --------------------------------------------------------------------- login
def rate_limited(ip: str) -> bool:
    now = time.time()
    hits = [t for t in _attempts.get(ip, []) if now - t < LOGIN_WINDOW]
    _attempts[ip] = hits
    return len(hits) >= LOGIN_MAX_TRIES


@app.get("/admin/login", response_class=HTMLResponse)
def login_form(request: Request):
    if current_user(request):
        return RedirectResponse("/admin", status_code=303)
    return tpl.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/admin/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(""), password: str = Form("")):
    ip = (request.headers.get("x-forwarded-for", "") or
          (request.client.host if request.client else "?")).split(",")[0].strip()

    if rate_limited(ip):
        return tpl.TemplateResponse(
            "login.html",
            {"request": request,
             "error": "For mange forsøg. Vent 15 minutter, og prøv igen."},
            status_code=429)

    time.sleep(0.4)                       # bremser gætteri en smule
    ok_user = secrets.compare_digest(username.strip(), ADMIN_USER)
    try:
        ok_pass = bcrypt.checkpw(password.encode(), ADMIN_HASH)
    except ValueError:
        ok_pass = False

    if not (ok_user and ok_pass):
        _attempts.setdefault(ip, []).append(time.time())
        return tpl.TemplateResponse(
            "login.html",
            {"request": request, "error": "Forkert brugernavn eller adgangskode."},
            status_code=401)

    _attempts.pop(ip, None)
    token = signer.dumps({"u": ADMIN_USER, "t": int(time.time())})
    resp = RedirectResponse("/admin", status_code=303)
    resp.set_cookie(COOKIE, token, max_age=SESSION_MAX_AGE, httponly=True,
                    secure=True, samesite="lax", path="/admin")
    return resp


@app.post("/admin/logout")
def logout(request: Request, csrf: str = Form("")):
    check_csrf(request, csrf)
    resp = RedirectResponse("/admin/login", status_code=303)
    resp.delete_cookie(COOKIE, path="/admin")
    return resp


# ---------------------------------------------------------------- oversigten
@app.get("/admin", response_class=HTMLResponse)
@app.get("/admin/", response_class=HTMLResponse)
def dashboard(request: Request, ok: str | None = None, err: str | None = None):
    require_user(request)
    return tpl.TemplateResponse("index.html", {
        "request": request, "posts": load_posts(), "csrf": csrf_of(request),
        "ok": ok, "err": err,
    })


@app.get("/admin/new", response_class=HTMLResponse)
def new_form(request: Request):
    require_user(request)
    return tpl.TemplateResponse("edit.html", {
        "request": request, "csrf": csrf_of(request), "slots": range(1, IMAGE_SLOTS + 1),
        "post": {"id": "", "date": date.today().isoformat(), "title": "",
                 "body": [], "images": []},
        "is_new": True,
    })


@app.get("/admin/edit/{post_id}", response_class=HTMLResponse)
def edit_form(request: Request, post_id: str):
    require_user(request)
    post = next((p for p in load_posts() if p["id"] == post_id), None)
    if not post:
        raise HTTPException(404, "Nyheden findes ikke.")
    return tpl.TemplateResponse("edit.html", {
        "request": request, "csrf": csrf_of(request), "slots": range(1, IMAGE_SLOTS + 1),
        "post": post, "is_new": False,
    })


# ----------------------------------------------------------------- billeder
SAFE_NAME = re.compile(r"^[a-z0-9]{8,32}\.(jpg|png)$")


def store_image(upload: FormUpload) -> str:
    """Gemmer et uploadet billede sikkert og returnerer filnavnet.

    Billedet bliver gen-kodet med Pillow. Det er med vilje: det bekræfter at
    filen virkelig er et billede, og det fjerner EXIF-data og alt andet, der
    måtte ligge i den oprindelige fil.
    """
    raw = upload.file.read(MAX_UPLOAD + 1)
    if len(raw) > MAX_UPLOAD:
        raise HTTPException(413, f"Billedet er for stort (højst {MAX_UPLOAD // 1024 // 1024} MB).")
    if not raw:
        raise HTTPException(400, "Den uploadede fil var tom.")

    import io
    try:
        probe = Image.open(io.BytesIO(raw))
        probe.verify()                              # kaster hvis det ikke er et billede
        img = Image.open(io.BytesIO(raw))           # verify() lukker filen, så åbn igen
        img.load()
    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(400, "Filen kunne ikke læses som et billede. "
                                 "Brug JPG eller PNG.")

    keep_png = img.format == "PNG" and img.mode in ("RGBA", "LA", "P")
    img = img.convert("RGBA" if keep_png else "RGB")
    img.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)

    IMG_DIR.mkdir(parents=True, exist_ok=True)
    name = secrets.token_hex(8) + (".png" if keep_png else ".jpg")
    dest = IMG_DIR / name
    if keep_png:
        img.save(dest, "PNG", optimize=True)
    else:
        img.save(dest, "JPEG", quality=84, optimize=True, progressive=True)
    return name


def drop_image(name: str) -> None:
    """Sletter et billede - kun hvis navnet er et af vores egne."""
    if not SAFE_NAME.match(name or ""):
        return
    target = (IMG_DIR / name).resolve()
    if target.parent == IMG_DIR.resolve() and target.is_file():
        target.unlink()


# --------------------------------------------------------------------- gem
@app.post("/admin/save")
async def save(request: Request):
    require_user(request)
    form = await request.form()
    check_csrf(request, str(form.get("csrf", "")))

    post_id = str(form.get("id", "")).strip()
    title = str(form.get("title", "")).strip()
    when = str(form.get("date", "")).strip()
    body_raw = str(form.get("body", ""))

    if not title:
        raise HTTPException(400, "Nyheden skal have en overskrift.")
    try:
        datetime.strptime(when, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(400, "Datoen skal skrives som ÅÅÅÅ-MM-DD.")

    # tom linje adskiller afsnit
    body = [" ".join(b.split()) for b in re.split(r"\n\s*\n", body_raw) if b.strip()]

    posts = load_posts()
    existing = next((p for p in posts if p["id"] == post_id), None) if post_id else None
    if post_id and not existing:
        raise HTTPException(404, "Nyheden findes ikke.")

    # billeder der allerede er på nyheden: behold, ret tekst, eller fjern
    images: list[dict] = []
    for i, old in enumerate(existing.get("images", []) if existing else []):
        if str(form.get(f"ex{i}_delete", "")):
            drop_image(old.get("file", "").split("/")[-1])
            continue
        images.append({
            "file": old["file"],
            "alt": str(form.get(f"ex{i}_alt", "")).strip()[:300],
            "caption": str(form.get(f"ex{i}_caption", "")).strip()[:300],
        })

    # nye billeder
    for n in range(1, IMAGE_SLOTS + 1):
        up = form.get(f"img{n}_file")
        if not isinstance(up, FormUpload) or not up.filename:
            continue
        stored = store_image(up)
        images.append({
            "file": f"{IMG_REL}/{stored}",
            "alt": str(form.get(f"img{n}_alt", "")).strip()[:300],
            "caption": str(form.get(f"img{n}_caption", "")).strip()[:300],
        })

    if existing:
        existing.update(date=when, title=title, body=body, images=images)
    else:
        new_id = f"{when}-{slugify(title)}"
        taken = {p["id"] for p in posts}
        while new_id in taken:
            new_id += "-2"
        posts.append({"id": new_id, "date": when, "title": title,
                      "body": body, "images": images})

    save_posts(posts)
    ok, log = publish()
    if not ok:
        print("PUBLISH FEJLEDE:\n" + log, flush=True)
        return RedirectResponse(
            "/admin?err=Nyheden+blev+gemt%2C+men+siden+kunne+ikke+bygges."
            "+Kontakt+webmasteren.", status_code=303)
    return RedirectResponse("/admin?ok=Nyheden+er+gemt+og+siden+er+opdateret.",
                            status_code=303)


@app.post("/admin/delete/{post_id}")
async def delete(request: Request, post_id: str, csrf: str = Form("")):
    require_user(request)
    check_csrf(request, csrf)

    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        raise HTTPException(404, "Nyheden findes ikke.")
    for im in post.get("images", []):
        drop_image(im.get("file", "").split("/")[-1])
    save_posts([p for p in posts if p["id"] != post_id])

    ok, log = publish()
    if not ok:
        print("PUBLISH FEJLEDE:\n" + log, flush=True)
    return RedirectResponse("/admin?ok=Nyheden+er+slettet.", status_code=303)


@app.post("/admin/rebuild")
async def rebuild(request: Request, csrf: str = Form("")):
    """Nødknap: byg siden igen uden at ændre indhold."""
    require_user(request)
    check_csrf(request, csrf)
    ok, log = publish()
    if not ok:
        print("PUBLISH FEJLEDE:\n" + log, flush=True)
        return RedirectResponse("/admin?err=Siden+kunne+ikke+bygges.", status_code=303)
    return RedirectResponse("/admin?ok=Siden+er+bygget+igen.", status_code=303)


@app.get("/admin/health")
def health():
    return {"ok": True, "posts": len(load_posts())}


# ================================================================== PARTIER
# Partiarkivet er kun for administratorer - det ligger under /admin og bliver
# aldrig bygget ind i den offentlige, statiske side.
from admin.pgn import GameStore                                    # noqa: E402

games = GameStore(SITE_DIR)


@app.get("/admin/partier", response_class=HTMLResponse)
def games_list(request: Request, ok: str | None = None, err: str | None = None):
    require_user(request)
    return tpl.TemplateResponse("games.html", {
        "request": request, "games": games.index(), "csrf": csrf_of(request),
        "ok": ok, "err": err,
    })


@app.post("/admin/partier/import")
async def games_import(request: Request):
    require_user(request)
    form = await request.form()
    check_csrf(request, str(form.get("csrf", "")))

    text = ""
    up = form.get("pgn_file")
    if isinstance(up, FormUpload) and up.filename:
        raw = up.file.read(4 * 1024 * 1024 + 1)
        if len(raw) > 4 * 1024 * 1024:
            raise HTTPException(413, "PGN-filen er for stor (højst 4 MB).")
        for enc in ("utf-8", "latin-1"):
            try:
                text = raw.decode(enc)
                break
            except UnicodeDecodeError:
                continue
    if not text.strip():
        text = str(form.get("pgn_text", ""))
    if not text.strip():
        raise HTTPException(400, "Vælg en PGN-fil, eller indsæt PGN-tekst.")

    try:
        added, warnings = games.add_from_pgn(text)
    except ValueError as e:
        raise HTTPException(400, str(e))

    from urllib.parse import quote
    if not added:
        msg = "Der blev ikke fundet nogen partier i det indsendte."
        if warnings:
            msg += " " + warnings[0]
        return RedirectResponse(f"/admin/partier?err={quote(msg)}", status_code=303)

    msg = f"{added} parti{'' if added == 1 else 'er'} importeret."
    if warnings:
        msg += f" {len(warnings)} advarsel{'' if len(warnings) == 1 else 'ler'}: {warnings[0]}"
    return RedirectResponse(f"/admin/partier?ok={quote(msg)}", status_code=303)


@app.get("/admin/parti/{game_id}", response_class=HTMLResponse)
def game_view(request: Request, game_id: str):
    require_user(request)
    game = games.get(game_id)
    if not game:
        raise HTTPException(404, "Partiet findes ikke.")
    return tpl.TemplateResponse("game.html", {
        "request": request, "game": game, "csrf": csrf_of(request),
        # JSON'en lægges i et <script>-element. En PGN-kommentar kunne indeholde
        # "</script>", så "<" escapes - < er gyldig JSON og læses tilbage
        # som "<", men kan ikke lukke elementet.
        "game_json": json.dumps({
            "start_fen": game["start_fen"],
            "moves": [{k: m[k] for k in ("ply", "san", "from", "to", "fen", "comment")}
                      for m in game["moves"]],
        }, ensure_ascii=False).replace("<", "\\u003c"),
    })


@app.post("/admin/parti/{game_id}/slet")
async def game_delete(request: Request, game_id: str, csrf: str = Form("")):
    require_user(request)
    check_csrf(request, csrf)
    if not games.delete(game_id):
        raise HTTPException(404, "Partiet findes ikke.")
    return RedirectResponse("/admin/partier?ok=Partiet+er+slettet.", status_code=303)


@app.get("/admin/parti/{game_id}/pgn")
def game_pgn(request: Request, game_id: str):
    """Henter den oprindelige PGN igen, så intet går tabt ved importen."""
    require_user(request)
    game = games.get(game_id)
    if not game:
        raise HTTPException(404, "Partiet findes ikke.")
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(
        game["pgn"], media_type="application/x-chess-pgn",
        headers={"Content-Disposition": f'attachment; filename="{game_id}.pgn"'})
