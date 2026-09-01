#!/usr/bin/env python3
"""
Statisk site-generator for Årslev Skakklub.

Kør:  python3 build.py
Den skriver .html-filerne i rodmappen ud fra skabelonen og indholdet nedenfor.
Al tekst er hentet fra klubbens tidligere Wix-side.
"""
from datetime import date
import html as H
import pathlib

SITE = "https://www.arslevskak.duckdns.org"
CLUB = "Årslev Skakklub"
BUILT = date.today().isoformat()

# ---------------------------------------------------------------- navigation
NAV = [
    ("index.html", "Forside"),
    ("nyheder.html", "Nyheder"),
    ("kalender.html", "Kalender"),
    ("turneringer.html", "Turneringer"),
    ("klubben.html", "Klubben"),
    ("info.html", "Info & kontakt"),
]

# ---------------------------------------------------------------- kontaktdata
BOARD = [
    ("Formand", "Lean Schier", "27264507", "lean@schier.dk"),
    ("Kasserer", "Søren Christensen", "23618513", "grimstrup.christensen@gmail.com"),
    ("Sekretær", "Jens Lund", "22614575", "jl.od@hotmail.com"),
]
VENUE = "Husmandsstedet, Over Bækken 1, 5792 Årslev"
MAPQ = "Over+B%C3%A6kken+1,+5792+%C3%85rslev"

# ---------------------------------------------------------------- kalender
# (uge, dato ISO, aktivitet, type)  type: klub | hurtig | hold | social | fri
CAL_AUTUMN = [
    (36, "2026-08-31", "Opstart og generalforsamling", "social"),
    (37, "2026-09-07", "Klubmatch mod OS – 1", "klub"),
    (38, "2026-09-14", "Klubmatch mod OS – 2", "klub"),
    (39, "2026-09-21", "Hurtigturnering, parti 1–3 af 9", "hurtig"),
    (40, "2026-09-28", "Klubmatch mod OS – 3", "klub"),
    (41, "2026-10-05", "Klubmatch mod OS – 4", "klub"),
    (42, "2026-10-12", "Hurtigturnering, parti 4–6 af 9", "hurtig"),
    (43, "2026-10-19", "Holdkamp 1", "hold"),
    (44, "2026-10-26", "Hurtigturnering, parti 7–9 af 9", "hurtig"),
    (45, "2026-11-02", "Klubturnering 1", "klub"),
    (46, "2026-11-09", "Holdkamp 2", "hold"),
    (47, "2026-11-16", "Klubturnering 2", "klub"),
    (48, "2026-11-23", "Klubturnering 3", "klub"),
    (49, "2026-11-30", "Holdkamp 3", "hold"),
    (50, "2026-12-07", "Klubturnering 4", "klub"),
    (51, "2026-12-14", "Juleafslutning", "social"),
    (52, "2026-12-21", "Fri", "fri"),
    (53, "2026-12-28", "Fri", "fri"),
]
TAGS = {
    "klub": ("tag", "Klubturnering"),
    "hurtig": ("tag", "Hurtigskak"),
    "hold": ("tag match", "Holdkamp"),
    "social": ("tag social", "Klubaften"),
    "fri": ("tag free", "Fri"),
}
MONTHS = ["", "januar", "februar", "marts", "april", "maj", "juni",
          "juli", "august", "september", "oktober", "november", "december"]
MONTHS_SHORT = ["", "jan", "feb", "mar", "apr", "maj", "jun",
                "jul", "aug", "sep", "okt", "nov", "dec"]


def dk_date(iso, short=False):
    y, m, d = (int(x) for x in iso.split("-"))
    mm = MONTHS_SHORT[m] if short else MONTHS[m]
    return f"{d}. {mm} {y}"


# ---------------------------------------------------------------- nyheder
NEWS = [
    dict(iso="2026-08-01", title="Kalenderen er opdateret",
         body=["""De 4 mandage, hvor vi skal spille OS-turnering, foregår jo inde i OS,
                  og der er ikke skak i Årslev de aftener.""",
               "Mere info omkring dette til GF."]),
    dict(iso="2026-05-12", title="Jan er årets lynmester – og ny sæson i nye lokaler",
         body=["""Som sidste aktivitet i den forgangne sæson afholdt vi i går vores afslutning,
                  hvor det vigtigste punkt var at finde årets lynmester. Lidt skuffende var vi
                  kun 7 mand, men der var vist noget med noget sygdom. Vi kastede os ud i en
                  dobbeltrundig alle mod alle, 14 runder, og titlen var der aldrig tvivl om:
                  Jan trampede hen over os alle sammen og vandt med 13/14. Tillykke!""",
               """Selvom der står én mandag mere i kalenderen, var dette sidste aften i sæsonen.
                  Næste begivenhed er sommerskak hos Søren, flyttet til 9. aug., og I skulle
                  have fået indbydelsen.""",
               """Den nye sæson starter mandag 31/8 (uge 36) – i nye lokaler! Det er på
                  Husmandsstedet, og adressen er Over Bækken 1.""",
               """Kalenderen er ikke så brugbar endnu, blandt andet fordi træningsturneringen
                  mod OS ikke ligger klar. Men noget er der da dato på: Opstart og
                  generalforsamling. Og det er dejligt nemt, det er nemlig samme dato:
                  mandag 31/8 kl. 19.00. Der kommer en indbydelse senest 14 dage før.""",
               "Fortsat god sommer til jer alle sammen!"]),
]

# ------------------------------------------------- klubturneringens rundeskema
PLAYERS = ["Erdem", "Jens", "Bent", "Knud", "Jan", "Henrik",
           "Niels", "Søren", "Magnus", "Ivar", "Lean", "Bye"]
# Bergerskema, 11 runder alle-mod-alle (12 pladser, én bye).
# Tal = modstanderens nummer i den pågældende runde.
BERGER = [
    [12, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    [11, 1, 12, 3, 4, 5, 6, 7, 8, 9, 10],
    [10, 11, 1, 2, 12, 4, 5, 6, 7, 8, 9],
    [9, 10, 11, 1, 2, 3, 12, 5, 6, 7, 8],
    [8, 9, 10, 11, 1, 2, 3, 4, 12, 6, 7],
    [7, 8, 9, 10, 11, 1, 2, 3, 4, 5, 12],
    [6, 12, 8, 9, 10, 11, 1, 2, 3, 4, 5],
    [5, 6, 7, 12, 9, 10, 11, 1, 2, 3, 4],
    [4, 5, 6, 7, 8, 12, 10, 11, 1, 2, 3],
    [3, 4, 5, 6, 7, 8, 9, 12, 11, 1, 2],
    [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 1],
    [1, 7, 2, 8, 3, 9, 4, 10, 5, 11, 6],
]

# ---------------------------------------------------------------- skabelon
def header(active, dark_top=False):
    parts = []
    for u, t in NAV:
        cur = ' aria-current="page"' if u == active else ''
        parts.append(f'      <li><a href="{u}"{cur}>{t}</a></li>\n')
    links = "".join(parts)
    return f"""<a class="skip" href="#main">Spring til indhold</a>
<header class="site-header" id="siteHeader">
  <div class="wrap nav">
    <a class="brand" href="index.html">
      <img src="assets/img/logo-192.png" width="44" height="44" alt="{CLUB}s logo">
      <span class="brand-text"><b>Årslev Skakklub</b><span>Stiftet 1982 · Fyn</span></span>
    </a>
    <button class="burger" id="burger" aria-expanded="false" aria-controls="navLinks" aria-label="Åbn menu"><span></span></button>
    <ul class="nav-links" id="navLinks">
{links}      <li><a class="nav-cta" href="info.html#bliv-medlem">Kom og spil</a></li>
    </ul>
  </div>
</header>
<div class="board-strip" aria-hidden="true"></div>"""


def footer():
    navls = "".join(f'<li><a href="{u}">{t}</a></li>' for u, t in NAV)
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <a class="brand" href="index.html">
          <img src="assets/img/logo-192.png" width="44" height="44" alt="">
          <span class="brand-text"><b>Årslev Skakklub</b><span>Stiftet 1982 · Fyn</span></span>
        </a>
        <p class="about">En lille, hyggelig skakklub i Faaborg-Midtfyn Kommune.
           Vi spiller hver mandag kl. 19.00 – alle er velkomne, uanset niveau, køn og alder.</p>
      </div>
      <div>
        <h4>Sider</h4>
        <ul>{navls}</ul>
      </div>
      <div>
        <h4>Kontakt</h4>
        <ul>
          <li>{VENUE}</li>
          <li>Mandag kl. 19.00</li>
          <li><a href="tel:+4527264507">27 26 45 07</a> · Lean Schier</li>
          <li><a href="mailto:lean@schier.dk">lean@schier.dk</a></li>
        </ul>
      </div>
    </div>
    <div class="foot-bottom">
      <span>© 1982–2026 {CLUB}</span>
      <span><a href="vedtaegter.html">Vedtægter</a> · <a href="privatlivspolitik.html">Privatlivspolitik</a></span>
    </div>
  </div>
</footer>"""


def page(slug, title, desc, body, active=None):
    active = active or slug
    doc = f"""<!DOCTYPE html>
<html lang="da">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#14110d">
<link rel="canonical" href="{SITE}/{slug}">
<link rel="icon" href="assets/img/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="assets/img/logo-192.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{CLUB}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{SITE}/{slug}">
<meta property="og:image" content="{SITE}/assets/img/logo-512.png">
<meta property="og:locale" content="da_DK">
<meta name="twitter:card" content="summary">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
{header(active)}
<main id="main">
{body}
</main>
{footer()}
<script src="assets/js/events.js" defer></script>
<script src="assets/js/main.js" defer></script>
</body>
</html>
"""
    pathlib.Path(slug).write_text(doc, encoding="utf-8")
    print(f"  → {slug} ({len(doc)//1024} kB)")


def page_head(kicker, h1, lede, crumb=True):
    cr = f'<p class="crumbs"><a href="index.html">Forside</a> / {kicker}</p>' if crumb else ""
    return f"""<section class="page-head">
  <div class="wrap">
    {cr}
    <h1>{h1}</h1>
    <p>{lede}</p>
  </div>
</section>"""


# ================================================================ FORSIDE
def cal_rows(items, limit=None):
    rows = []
    for uge, iso, akt, typ in (items[:limit] if limit else items):
        cls, label = TAGS[typ]
        rows.append(
            f'      <tr data-date="{iso}"><td>{uge}</td><td>{dk_date(iso)}</td>'
            f'<td class="wide">{akt}</td><td><span class="{cls}">{label}</span></td></tr>'
        )
    return "\n".join(rows)


def build_index():
    news = "\n".join(f"""      <article class="post reveal">
        <div class="when"><b>{int(n['iso'][8:])}. {MONTHS_SHORT[int(n['iso'][5:7])]}</b><span>{n['iso'][:4]}</span></div>
        <div>
          <h3>{n['title']}</h3>
          <p>{' '.join(n['body'][0].split())}</p>
          <a class="more" href="nyheder.html" style="color:var(--gold);font-weight:600;text-decoration:none">Læs hele nyheden →</a>
        </div>
      </article>""" for n in NEWS[:2])

    body = f"""<section class="hero">
  <div class="wrap">
    <div>
      <p class="eyebrow"><span class="dot"></span> Ny sæson · mandag 31. august 2026</p>
      <h1>Er du en <em>sovende skak‑ulv?</em></h1>
      <p class="lede">Du har måske spillet skak tidligere, spiller online eller husker tilbage på
         hyggespil med din bedstefar i barndommen? Fascinationen af spillet ligger latent og
         ulmer i bevidstheden. Hvorfor ikke hygge sig i et fællesskab med ligesindede?</p>
      <div class="hero-actions">
        <a class="btn btn-gold" href="info.html#bliv-medlem">Kom og spil med</a>
        <a class="btn btn-ghost" href="kalender.html">Se sæsonens program</a>
      </div>
      <div class="hero-facts">
        <div><b>1982</b><small>Stiftet</small></div>
        <div><b>12</b><small>Medlemmer</small></div>
        <div><b>Serie&nbsp;1</b><small>Holdturnering</small></div>
        <div><b>Mandag</b><small>Kl. 19.00</small></div>
      </div>
    </div>
    <div class="hero-art">
      <img src="assets/img/logo-512.png" width="512" height="512" alt="{CLUB}s logo: en springer i sort og guld" fetchpriority="high">
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="nextup reveal" id="nextup" hidden>
      <div>
        <p class="lbl" style="margin:0 0 4px">Næste klubaften</p>
        <div class="ev" id="nextEvent">—</div>
      </div>
      <div class="spacer"></div>
      <div class="dt" id="nextDate"></div>
      <a class="btn btn-gold" href="kalender.html">Hele kalenderen</a>
    </div>
  </div>
</section>

<section class="tint">
  <div class="wrap">
    <div class="sec-head center">
      <p class="kicker">Velkommen</p>
      <h2>En skakklub er ikke en lukket, højpandet loge</h2>
      <p>… men „blot“ et inkluderende socialt fællesskab med skakspillet som omdrejningspunkt.
         Alle kan være med uanset niveau, køn og alder.</p>
    </div>
    <div class="grid g3">
      <div class="card hover reveal">
        <div class="ico" aria-hidden="true">♟</div>
        <h3>Hygge frem for alvor</h3>
        <p>Vi er en lille, hyggelig skakklub i Faaborg‑Midtfyn Kommune på Fyn. Klubben blev
           stiftet i 1982, og vi er p.t. 12 medlemmer.</p>
      </div>
      <div class="card hover reveal">
        <div class="ico" aria-hidden="true">♞</div>
        <h3>Turneringer hele sæsonen</h3>
        <p>Vi hygger os med klubturnering, hurtigskak, venskabskampe m.m. – og spiller med i
           Fyns Skak Unions holdturnering i serie 1 i sæson 2026/2027.</p>
      </div>
      <div class="card hover reveal">
        <div class="ico" aria-hidden="true">♜</div>
        <h3>Prøv en måned gratis</h3>
        <p>Du kan helt uforpligtende se klubben an og spille med den første måneds tid.
           Ingen tilmelding, ingen forpligtelser.</p>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head">
      <p class="kicker">Praktisk</p>
      <h2>Sådan finder du os</h2>
      <p>Årslev Skakklub lukker dørene op for den nye sæson i nye, hyggelige spillelokaler
         på Husmandsstedet den 31. august 2026.</p>
    </div>
    <div class="grid g2">
      <div class="grid g2" style="align-content:start">
        <div class="card reveal">
          <div class="ico" aria-hidden="true">📍</div>
          <h3>Spillested</h3>
          <p>Husmandsstedet<br>Over Bækken 1<br>5792 Årslev</p>
          <a class="more" style="color:var(--gold);font-weight:600;text-decoration:none"
             href="https://www.google.com/maps/search/?api=1&amp;query={MAPQ}" target="_blank" rel="noopener">Vis på kort →</a>
        </div>
        <div class="card reveal">
          <div class="ico" aria-hidden="true">🕖</div>
          <h3>Klubaften</h3>
          <p>Hver mandag kl. 19.00 i sæsonen. Ring gerne først, så du ikke går forgæves
             pga. holdskak m.v.</p>
        </div>
        <div class="card reveal">
          <div class="ico" aria-hidden="true">💳</div>
          <h3>Kontingent</h3>
          <p>Seniorer 450 kr. pr. halvår.<br>Pensionister og juniorer 400 kr. pr. halvår.</p>
        </div>
        <div class="card reveal">
          <div class="ico" aria-hidden="true">☎</div>
          <h3>Kontakt</h3>
          <p><a href="tel:+4527264507" style="color:var(--gold);text-decoration:none;font-weight:600">27 26 45 07</a><br>
             Lean Schier, formand</p>
        </div>
      </div>
      <div class="reveal">
        <a class="map-card" href="https://www.google.com/maps/search/?api=1&amp;query={MAPQ}"
           target="_blank" rel="noopener">
          <img src="assets/img/kort.png" width="1000" height="750" loading="lazy"
               alt="Kort over spillestedet Over Bækken 1 i Sønder Nærå ved Årslev">
          <span class="map-pill">Åbn i Google Maps →</span>
        </a>
        <p class="map-credit">Kortdata © <a href="https://www.openstreetmap.org/copyright"
           target="_blank" rel="noopener">OpenStreetMap-bidragydere</a></p>
      </div>
    </div>
  </div>
</section>

<section class="tint">
  <div class="wrap">
    <div class="sec-head"><p class="kicker">Nyheder</p><h2>Seneste nyt fra klubben</h2></div>
    <div class="news">
{news}
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head"><p class="kicker">Efterår 2026</p><h2>De næste klubaftener</h2>
      <p>Vi spiller mandage kl. 19.00. Bemærk: de fire mandage, hvor vi skal spille
         OS‑turnering, foregår inde i OS – der er ikke skak i Årslev de aftener.</p></div>
    <div class="table-scroll reveal">
      <table>
        <thead><tr><th>Uge</th><th>Dato</th><th>Aktivitet</th><th>Type</th></tr></thead>
        <tbody>
{cal_rows(CAL_AUTUMN, 8)}
        </tbody>
      </table>
    </div>
    <p style="margin-top:22px"><a class="btn btn-outline" href="kalender.html">Se hele sæsonen</a></p>
  </div>
</section>

<section class="tint">
  <div class="wrap">
    <div class="callout reveal">
      <h3>Støt Årslev Skakklub – gratis</h3>
      <p>Du kan støtte klubben ved at tilmelde dig <strong>Fynsk Support El &amp; Gas</strong>, som
         udløser 2 øre pr. kWh og 6 øre pr. m³ gas til klubben, uden at det koster dig ekstra.</p>
      <p><a class="btn btn-dark" href="https://www.energifyn.dk/privat/fynsk-support/" target="_blank" rel="noopener">Gå til Energi Fyn →</a></p>
    </div>
  </div>
</section>

<section class="cta-band">
  <div class="wrap">
    <h2>Har du lyst til at spille skak?</h2>
    <p>Så er du velkommen hos os mandag kl. 19.00. Kontakt os gerne inden på 27 26 45 07
       (Lean Schier), så du ikke kommer til at gå forgæves pga. holdskak m.v.</p>
    <div class="btns">
      <a class="btn btn-gold" href="tel:+4527264507">Ring 27 26 45 07</a>
      <a class="btn btn-ghost" href="mailto:lean@schier.dk">Send en mail</a>
    </div>
  </div>
</section>"""
    page("index.html", f"{CLUB} – hyggeskak på Midtfyn hver mandag",
         "Årslev Skakklub er en lille, hyggelig skakklub i Faaborg-Midtfyn Kommune. "
         "Vi spiller hver mandag kl. 19.00 på Husmandsstedet, Over Bækken 1, 5792 Årslev. "
         "Alle er velkomne uanset niveau.", body)


# ================================================================ NYHEDER
def build_nyheder():
    posts = []
    for n in NEWS:
        paras = "\n          ".join(f"<p>{' '.join(p.split())}</p>" for p in n["body"])
        posts.append(f"""      <article class="post reveal" id="n{n['iso']}">
        <div class="when"><b>{int(n['iso'][8:])}. {MONTHS_SHORT[int(n['iso'][5:7])]}</b><span>{n['iso'][:4]}</span></div>
        <div>
          <h3>{n['title']}</h3>
          {paras}
        </div>
      </article>""")
    body = page_head("Nyheder", "Nyheder", "Meddelelser, resultater og praktisk info til medlemmerne.") + f"""
<section>
  <div class="wrap">
    <div class="news">
{chr(10).join(posts)}
    </div>
    <div class="callout reveal" style="margin-top:34px">
      <h3>Klubbens gamle blog</h3>
      <p>Ældre indlæg og partier ligger fortsat på klubbens blog.</p>
      <p><a class="btn btn-dark" href="https://aarslevskakblog.blogspot.com/" target="_blank" rel="noopener">Åbn bloggen →</a></p>
    </div>
  </div>
</section>"""
    page("nyheder.html", f"Nyheder – {CLUB}",
         "Seneste nyheder fra Årslev Skakklub: sæsonstart, klubmesterskaber og kalenderændringer.",
         body)


# ================================================================ KALENDER
def build_kalender():
    body = page_head("Kalender", "Sæsonkalender 2026/2027",
        "Vi spiller mandage kl. 19.00 på Husmandsstedet, Over Bækken 1, 5792 Årslev. "
        "Dagens aktivitet fremgår nedenfor – kalenderen opdateres i løbet af sæsonen.") + f"""
<section>
  <div class="wrap">
    <div class="nextup reveal" id="nextup" hidden>
      <div>
        <p class="lbl" style="margin:0 0 4px">Næste klubaften</p>
        <div class="ev" id="nextEvent">—</div>
      </div>
      <div class="spacer"></div>
      <div class="dt" id="nextDate"></div>
    </div>

    <div class="sec-head" style="margin-top:44px"><p class="kicker">Efterår 2026</p><h2>Efterårssæsonen</h2>
      <p>Bemærk: de 4 mandage, hvor vi skal spille OS‑turnering, foregår inde i OS,
         og der er ikke skak i Årslev de aftener.</p></div>
    <div class="table-scroll reveal">
      <table id="calTable">
        <caption>Mandage kl. 19.00 · uge 36–53, 2026</caption>
        <thead><tr><th>Uge</th><th>Dato</th><th>Aktivitet</th><th>Type</th></tr></thead>
        <tbody>
{cal_rows(CAL_AUTUMN)}
        </tbody>
      </table>
    </div>

    <div class="sec-head" style="margin-top:56px"><p class="kicker">Forår 2027</p><h2>Forårssæsonen</h2></div>
    <div class="card reveal">
      <p style="margin:0">Programmet for foråret 2027 er endnu ikke lagt fast. Det bliver
         offentliggjort her, så snart holdkampe og turneringsplaner er på plads –
         blandt andet afventer vi datoerne fra Fyns Skak Union.</p>
    </div>

    <div class="grid g2" style="margin-top:44px">
      <div class="card reveal">
        <div class="ico" aria-hidden="true">📅</div>
        <h3>Sommerskak hos Søren</h3>
        <p>Et tilbagevendende højdepunkt siden ca. 2016: skak, snak og spisning, som Søren
           venligst er vært for. Vi spiller typisk et par hurtigskakturneringer afbrudt af
           en frokostpause. Bent eller Søren sender indbydelse ud – hold øje med postkassen
           og meld jer til.</p>
      </div>
      <div class="card reveal">
        <div class="ico" aria-hidden="true">🏆</div>
        <h3>Holdturneringen</h3>
        <p>Vi stiller op i Fyns Skak Unions holdturnering i serie 1 i sæson 2026/2027.
           Stillinger og runder følges på Dansk Skak Unions holdturneringsside.</p>
        <p><a class="more" style="color:var(--gold);font-weight:600;text-decoration:none"
              href="https://holdskak.skak.dk/" target="_blank" rel="noopener">holdskak.skak.dk →</a></p>
      </div>
    </div>
  </div>
</section>"""
    page("kalender.html", f"Kalender 2026/2027 – {CLUB}",
         "Sæsonkalender for Årslev Skakklub 2026/2027. Klubaftener hver mandag kl. 19.00 "
         "med klubturnering, hurtigskak og holdkampe.", body)


# ================================================================ TURNERINGER
def build_turneringer():
    # rundeskema
    head = "".join(f"<th>{r}</th>" for r in range(1, 12))
    rows = []
    for i, (name, sched) in enumerate(zip(PLAYERS[:-1], BERGER[:-1]), start=1):
        cells = "".join(f"<td>{PLAYERS[o-1] if o != 12 else '—'}</td>" for o in sched)
        rows.append(f"<tr><td>{i}</td><td>{name}</td>{cells}</tr>")
    cross = f"""    <div class="table-scroll reveal">
      <table class="crosstable">
        <caption>Bergerskema: modstander i hver af de 11 runder. „—“ betyder oversidder.</caption>
        <thead><tr><th>Nr.</th><th>Navn</th>{head}</tr></thead>
        <tbody>
        {chr(10).join('        ' + r for r in rows)}
        </tbody>
      </table>
    </div>"""

    body = page_head("Turneringer", "Turneringer",
        "Klubturnering, hurtigskakmesterskab, holdturnering og de årlige klassikere. "
        "Sådan spiller vi i Årslev.") + f"""
<section>
  <div class="wrap">
    <div class="grid g2">
      <div class="card hover reveal">
        <div class="ico" aria-hidden="true">♛</div>
        <h3>Klubturneringen</h3>
        <p>Sæsonens hovedturnering. Vi spiller alle mod alle over 11 runder efter
           Bergerskemaet nedenfor. Vi forsøger at afvikle alle kampene, men da der også
           er noget, der hedder afbud, lader det sig næppe gøre. Hvis det mod slut viser sig
           nødvendigt, får de mest betydende kampe (for mesterskabet) højeste prioritet.</p>
        <p><strong>Afbud:</strong> man skal melde afbud, hvis man er forhindret –
           meget nødigt!</p>
      </div>
      <div class="card hover reveal">
        <div class="ico" aria-hidden="true">⚡</div>
        <h3>Hurtigskakmesterskabet</h3>
        <p>Sideløbende med klubturneringen spiller vi over 4 aftener om årets
           hurtigskakmesterskab – 9 partier fordelt på tre aftener i efteråret
           (parti 1–3, 4–6 og 7–9).</p>
      </div>
      <div class="card hover reveal">
        <div class="ico" aria-hidden="true">🛡</div>
        <h3>Holdturneringen</h3>
        <p>Vi spiller med i Fyns Skak Unions holdturnering i <strong>serie 1</strong> i sæson
           2026/2027, med tre holdkampe i efteråret (uge 43, 46 og 49).</p>
        <p><a class="more" style="color:var(--gold);font-weight:600;text-decoration:none"
              href="https://holdskak.skak.dk/" target="_blank" rel="noopener">Stillinger på holdskak.skak.dk →</a></p>
      </div>
      <div class="card hover reveal">
        <div class="ico" aria-hidden="true">🤝</div>
        <h3>Klubmatch mod OS</h3>
        <p>Sæsonen starter med en træningsturnering mod OS over fire mandage i september
           og oktober. De aftener foregår spillet inde i OS – der er derfor ikke skak i
           Årslev de pågældende mandage.</p>
      </div>
      <div class="card hover reveal">
        <div class="ico" aria-hidden="true">☀</div>
        <h3>Sommerskak</h3>
        <p>Et tilbagevendende højdepunkt siden ca. 2016: skak/snak/spise‑arrangementer hos
           Søren, typisk et par hurtigskakturneringer afbrudt af en frokostpause. Både
           gæster og juniorer fra andre klubber deltager.</p>
      </div>
      <div class="card hover reveal">
        <div class="ico" aria-hidden="true">🎄</div>
        <h3>Juleafslutning &amp; lynmesterskab</h3>
        <p>Sæsonen rammes ind af juleafslutning i december og en afslutningsaften i maj,
           hvor årets lynmester findes i en dobbeltrundig alle‑mod‑alle. Regerende
           lynmester: <strong>Jan</strong> med 13/14.</p>
      </div>
    </div>

    <div class="callout reveal" style="margin-top:40px">
      <h3>Præmier</h3>
      <ul style="margin:0;padding-left:1.2em">
        <li>Klubturneringen, 1. plads i gruppe A1: 200 kr.</li>
        <li>Klubturneringen, 1. plads i gruppe A2: 100 kr.</li>
        <li>Hurtigskak, nr. 1: en sixpack el. lignende.</li>
        <li>Lynmesterskabet, nr. 1: en sixpack el. lignende.</li>
      </ul>
    </div>
  </div>
</section>

<section class="tint">
  <div class="wrap">
    <div class="sec-head"><p class="kicker">Klubturneringen</p><h2>Rundeskema</h2>
      <p>11 runder alle mod alle. Med 11 spillere sidder én over i hver runde.
         Skemaet er udgangspunktet – afbud og resultater håndteres på klubaftenerne.</p></div>
{cross}
    <div class="grid g2" style="margin-top:34px">
      <div class="card reveal">
        <h3>Betænkningstid</h3>
        <p>45+0 pr. parti i dobbeltrunderne og 90+0 i de enkeltrunder, hvor der kun spilles
           ét langt parti.</p>
      </div>
      <div class="card reveal">
        <h3>Opvarmningsturnering</h3>
        <p>Sæsonen kan starte med en opvarmningsturnering over nogle aftener for de spillere,
           der er klar fra start. Resultaterne tæller ikke med i den „rigtige“ klubturnering.</p>
      </div>
    </div>
  </div>
</section>"""
    page("turneringer.html", f"Turneringer – {CLUB}",
         "Klubturnering over 11 runder, hurtigskakmesterskab, serie 1-holdturnering, "
         "sommerskak og lynmesterskab i Årslev Skakklub.", body)


# ================================================================ KLUBBEN
def build_klubben():
    members = "".join(f'<li>{m}</li>' for m in PLAYERS if m != "Bye")
    body = page_head("Klubben", "Om Årslev Skakklub",
        "Stiftet 24. februar 1982. En lille, hyggelig klub med skakspillet som "
        "omdrejningspunkt – og et socialt fællesskab som fundament.") + f"""
<section>
  <div class="wrap">
    <div class="grid g2">
      <div>
        <p class="kicker">Vores formål</p>
        <h2>Skak som fælles omdrejningspunkt</h2>
        <p>Klubbens formål er at udvikle og fremme kendskabet til og interessen for skakspillet
           gennem afholdelse af klubaftener med skaklige aktiviteter, herunder afvikling af en
           klubturnering, samt ved deltagelse i Fyns Skak Unions holdturneringer.</p>
        <p>I praksis betyder det en mandagsaften, hvor der bliver spillet seriøst skak – og
           snakket mindst lige så meget. En skakklub er ikke en lukket, højpandet loge, men
           „blot“ et inkluderende socialt fællesskab. Alle kan være med uanset niveau, køn
           og alder.</p>
        <p><a class="btn btn-outline" href="vedtaegter.html">Læs vedtægterne</a></p>
      </div>
      <div class="grid" style="align-content:start">
        <div class="card reveal"><div class="ico" aria-hidden="true">🏛</div>
          <h3>Stiftet 24. februar 1982</h3>
          <p>Klubben har hjemsted i Faaborg‑Midtfyn Kommune på Fyn. Vedtægterne blev vedtaget
             på generalforsamlingen 20. februar 1995 og senest ændret 15. september 2025.</p></div>
        <div class="card reveal"><div class="ico" aria-hidden="true">👥</div>
          <h3>12 medlemmer</h3>
          <p>Vi er en lille klub, og det er en del af charmen: man bliver hurtigt kendt,
             og der er altid en modstander at spille imod.</p></div>
      </div>
    </div>
  </div>
</section>

<section class="tint">
  <div class="wrap">
    <div class="sec-head"><p class="kicker">Bestyrelsen</p><h2>Hvem driver klubben</h2>
      <p>Bestyrelsen består af tre medlemmer, der vælges på den ordinære generalforsamling
         i september.</p></div>
    <div class="grid g3">
""" + "\n".join(f"""      <div class="card reveal">
        <div class="person">
          <div class="avatar" aria-hidden="true">{n.split()[0][0]}</div>
          <div>
            <p class="role" style="margin:0">{role}</p>
            <strong>{n}</strong>
            <a href="tel:+45{tel}">{tel[:2]} {tel[2:4]} {tel[4:6]} {tel[6:]}</a>
            <a href="mailto:{mail}">{mail}</a>
          </div>
        </div>
      </div>""" for role, n, tel, mail in BOARD) + f"""
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head"><p class="kicker">Traditioner</p><h2>Årets faste punkter</h2></div>
    <div class="grid g3">
      <div class="card hover reveal"><div class="ico" aria-hidden="true">🌞</div>
        <h3>Sommerskak</h3>
        <p>Et tilbagevendende højdepunkt siden ca. 2016. Det kan man roligt kalde de
           skak/snak/spise‑arrangementer, som Søren så venligt er vært for. Vi spiller typisk
           et par hurtigskakturneringer, afbrudt af en frokostpause.</p>
        <p>Bent eller Søren sender indbydelse ud, så hold øje med postkassen og meld jer til.</p></div>
      <div class="card hover reveal"><div class="ico" aria-hidden="true">🎁</div>
        <h3>Juleafslutning</h3>
        <p>Sidste klubaften før jul. Der har været en julekonkurrence, som deltagerne ikke
           altid vidste fandt sted – vinderen var den, der fandt det manglende gulfarvede ord.
           Præmie: en belgisk juleøl.</p></div>
      <div class="card hover reveal"><div class="ico" aria-hidden="true">⚡</div>
        <h3>Sæsonafslutning</h3>
        <p>Sæsonens sidste aften i maj afgør årets lynmester i en dobbeltrundig
           alle‑mod‑alle. I 2026 vandt Jan overlegent med 13 af 14 mulige point.</p></div>
    </div>

    <div class="card reveal" style="margin-top:34px">
      <h3>Medlemmer i klubturneringen</h3>
      <p style="color:var(--muted)">Deltagerne i den seneste klubturnering:</p>
      <ul style="columns:3;column-gap:28px;margin:0;padding-left:1.2em">{members}</ul>
    </div>
  </div>
</section>

<section class="cta-band">
  <div class="wrap">
    <h2>Bliv en del af klubben</h2>
    <p>Du kan helt uforpligtende se klubben an og spille med den første måneds tid.</p>
    <div class="btns">
      <a class="btn btn-gold" href="info.html#bliv-medlem">Sådan gør du</a>
      <a class="btn btn-ghost" href="kalender.html">Se kalenderen</a>
    </div>
  </div>
</section>"""
    page("klubben.html", f"Om klubben – {CLUB}",
         "Årslev Skakklub blev stiftet i 1982 og har hjemsted i Faaborg-Midtfyn Kommune. "
         "Læs om klubbens formål, bestyrelse og traditioner.", body)


# ================================================================ INFO
def build_info():
    board = "\n".join(f"""      <div class="card reveal">
        <div class="person">
          <div class="avatar" aria-hidden="true">{n.split()[0][0]}</div>
          <div>
            <p class="role" style="margin:0">{role}</p>
            <strong>{n}</strong>
            <a href="tel:+45{tel}">{tel[:2]} {tel[2:4]} {tel[4:6]} {tel[6:]}</a>
            <a href="mailto:{mail}">{mail}</a>
          </div>
        </div>
      </div>""" for role, n, tel, mail in BOARD)

    body = page_head("Info &amp; kontakt", "Info &amp; kontakt",
        "Spillested, klubaften, kontingent og bestyrelse – alt det praktiske samlet på én side.") + f"""
<section>
  <div class="wrap">
    <div class="grid g2">
      <div>
        <p class="kicker">Praktisk</p>
        <h2>Det praktiske</h2>
        <dl class="deflist reveal">
          <div><dt>Spillested</dt><dd>Husmandsstedet<br>Over Bækken 1<br>5792 Årslev<br>
            <a href="https://www.google.com/maps/search/?api=1&amp;query={MAPQ}" target="_blank" rel="noopener">Vis på kort →</a></dd></div>
          <div><dt>Klubaften</dt><dd>Mandag kl. 19.00</dd></div>
          <div><dt>Sæsonstart</dt><dd>Mandag 31. august 2026 – opstart og generalforsamling kl. 19.00</dd></div>
          <div><dt>Kontingent</dt><dd>Seniorer: 450 kr. pr. halvår<br>Pensionister og juniorer: 400 kr. pr. halvår</dd></div>
          <div><dt>Prøveperiode</dt><dd>Den første måneds tid er helt uforpligtende og gratis</dd></div>
          <div><dt>Hjemsted</dt><dd>Faaborg‑Midtfyn Kommune, Fyn</dd></div>
          <div><dt>Forbund</dt><dd>Fyns Skak Union · Dansk Skak Union</dd></div>
        </dl>
      </div>
      <div class="reveal">
        <a class="map-card" href="https://www.google.com/maps/search/?api=1&amp;query={MAPQ}"
           target="_blank" rel="noopener">
          <img src="assets/img/kort.png" width="1000" height="750" loading="lazy"
               alt="Kort over spillestedet Over Bækken 1 i Sønder Nærå ved Årslev">
          <span class="map-pill">Åbn i Google Maps →</span>
        </a>
        <p class="map-credit">Kortdata © <a href="https://www.openstreetmap.org/copyright"
           target="_blank" rel="noopener">OpenStreetMap-bidragydere</a></p>
      </div>
    </div>
  </div>
</section>

<section class="tint" id="bliv-medlem">
  <div class="wrap">
    <div class="sec-head"><p class="kicker">Bliv medlem</p><h2>Har du lyst til at spille skak?</h2>
      <p>Så er du velkommen hos os mandag kl. 19.00, men kontakt os gerne inden på
         27 26 45 07 (Lean Schier), så du ikke kommer til at gå forgæves pga. holdskak m.v.</p></div>
    <div class="grid g3">
      <div class="card reveal"><div class="ico" aria-hidden="true">1</div>
        <h3>Ring eller skriv</h3>
        <p>Giv formanden et kald på <a href="tel:+4527264507" style="color:var(--gold);font-weight:600;text-decoration:none">27 26 45 07</a>
           eller send en mail til <a href="mailto:lean@schier.dk" style="color:var(--gold);font-weight:600;text-decoration:none">lean@schier.dk</a>.</p></div>
      <div class="card reveal"><div class="ico" aria-hidden="true">2</div>
        <h3>Kom en mandag</h3>
        <p>Mød op kl. 19.00 på Husmandsstedet, Over Bækken 1. Du behøver ikke tage noget med
           – vi har brikker, brætter og ure.</p></div>
      <div class="card reveal"><div class="ico" aria-hidden="true">3</div>
        <h3>Prøv en måned</h3>
        <p>Du kan helt uforpligtende se klubben an og spille med den første måneds tid,
           før du beslutter dig.</p></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head"><p class="kicker">Bestyrelse</p><h2>Kontakt bestyrelsen</h2></div>
    <div class="grid g3">
{board}
    </div>

    <div class="grid g2" style="margin-top:40px">
      <div class="callout reveal">
        <h3>Støt klubben – uden at det koster dig noget</h3>
        <p>Du kan støtte Årslev Skakklub ved at tilmelde dig <strong>Fynsk Support El &amp; Gas</strong>,
           som udløser 2 øre pr. kWh og 6 øre pr. m³ gas til klubben, uden at det koster dig ekstra.</p>
        <p><a class="btn btn-dark" href="https://www.energifyn.dk/privat/fynsk-support/" target="_blank" rel="noopener">Gå til Energi Fyn →</a></p>
      </div>
      <div class="card reveal">
        <h3>Nyttige links</h3>
        <ul style="padding-left:1.2em;margin:0">
          <li><a href="https://holdskak.skak.dk/" target="_blank" rel="noopener">Holdturneringen – holdskak.skak.dk</a></li>
          <li><a href="https://skak.dk/" target="_blank" rel="noopener">Dansk Skak Union</a></li>
          <li><a href="https://fsu.skak.dk/" target="_blank" rel="noopener">Fyns Skak Union</a></li>
          <li><a href="https://aarslevskakblog.blogspot.com/" target="_blank" rel="noopener">Klubbens gamle blog</a></li>
          <li><a href="vedtaegter.html">Klubbens vedtægter</a></li>
          <li><a href="privatlivspolitik.html">Privatlivspolitik</a></li>
        </ul>
      </div>
    </div>
  </div>
</section>"""
    page("info.html", f"Info &amp; kontakt – {CLUB}",
         "Spillested, klubaften, kontingent og kontaktoplysninger for Årslev Skakklub. "
         "Husmandsstedet, Over Bækken 1, 5792 Årslev – mandag kl. 19.00.", body)


# ================================================================ VEDTÆGTER
VEDT = [
 ("§ 1. Navn, hjemsted og formål.", [
  "Klubbens navn er Årslev Skakklub og den har hjemsted i Faaborg-Midtfyn kommune.",
  "Klubbens formål er at udvikle og fremme kendskabet til og interessen for skakspillet gennem afholdelse af klubaftener med skaklige aktiviteter, herunder afvikling af en klubturnering, samt ved deltagelse i FSUs holdturneringer."]),
 ("§ 2. Medlemmer.", [
  "Som medlem kan optages enhver, som er interesseret i skak.",
  "Ind- og udmeldelse sker til formanden eller kassereren.",
  "Bestyrelsen kan ekskludere medlemmer, som modarbejder klubben eller som er i restance med kontingent."]),
 ("§ 3. Generalforsamlingen.", [
  "Generalforsamlingen er i alle anliggender klubbens højeste myndighed. Generalforsamlingen foretager valg af bestyrelsesmedlemmer, suppleanter og revisorer, samt træffer de for klubbens drift nødvendige beslutninger.",
  "Indkaldelse til generalforsamlinger sker skriftligt med angivelse af dagsordenen og indkaldelsen skal enten være fremlagt på spillestedet eller rundsendt til samtlige medlemmer pr. mail senest 2 uger før afholdelsen.",
  "Forslag, som ønskes behandlet på generalforsamlingen, skal være formanden i hænde senest 1 uge før generalforsamlingen.",
  "Generalforsamlingen er beslutningsdygtig uanset antallet af fremmødte medlemmer. Afstemninger sker ved håndsoprækning, men skal ske skriftligt, hvis blot et medlem ønsker dette.",
  "Beslutninger træffes ved alm. stemmeflertal. Til ændring af klubbens vedtægter kræves dog, at mindst 2/3 af de fremmødte stemmer for forslaget.",
  "Om forhandlinger og beslutninger på generalforsamlingen udfærdiger bestyrelsen et kort referat, som skal være tilgængelig for alle klubbens medlemmer."]),
 ("§ 4. Ordinær generalforsamling.", [
  "Ordinær generalforsamling afholdes hvert år i september måned.",
  ("Dagsordenen skal mindst indeholde følgende punkter:",
   ["Valg af dirigent.", "Formandens beretning.", "Fremlæggelse af årsregnskab.",
    "Fastsættelse af kontingent.", "Indkomne forslag.",
    "Valg til bestyrelsen i henhold til § 5, stk. 1.",
    "Valg af suppleant i henhold til § 5, stk. 2.",
    "Valg af revisorer i henhold til § 5, stk. 3.", "Eventuelt."])]),
 ("§ 5. Valg m.v.", [
  "Der vælges 3 bestyrelsesmedlemmer, almindeligvis for 2 år ad gangen. De 2 medlemmer afgår i lige år og 1 medlem i ulige år.",
  "Der vælges 1 bestyrelsessuppleant for 1 år ad gangen.",
  "Der vælges 2 revisorer for 1 år ad gangen.",
  "Alle klubbens medlemmer er forpligtet til at modtage valg. Genvalg kan finde sted.",
  "Valg mellem flere kandidater, end der er ledige pladser, sker skriftligt ved angivelse af højst det antal navne, der svarer til antallet af pladser. De kandidater, der får flest stemmer er valgt, og den efterfølgende er evt. suppleant."]),
 ("§ 6. Ekstraordinær generalforsamling.", [
  "Ekstraordinær generalforsamling afholdes, når bestyrelsen finder anledning hertil, eller når mindst 1/3 af klubbens medlemmer skriftligt fremsætter ønske herom.",
  "Ekstraordinær generalforsamling efter medlemsønske skal afholdes senest 4 uger efter ønskets fremsættelse."]),
 ("§ 7. Bestyrelsen.", [
  "Bestyrelsen varetager klubbens daglige ledelse og træffer herunder bestemmelse om anvendelse af foreningens midler.",
  "Bestyrelsen konstituerer sig selv. Posterne som formand og kasserer skal altid fordeles.",
  "Udtræder et bestyrelsesmedlem i utide, indtræder suppleanten i bestyrelsen frem til den førstkommende generalforsamling.",
  ("__SKIP__", None),
  "Bestyrelsesmøde afholdes, når formanden finder anledning hertil eller når 1 bestyrelsesmedlem fremsætter ønske herom.",
  "Beslutninger i bestyrelsen træffes ved alm. stemmeflertal. Ved stemmelighed er formandens stemme afgørende.",
  "Bestyrelsesbeslutninger af væsentlig karakter dokumenteres i en beslutningsprotokol."]),
 ("§ 8. Regnskabet.", [
  "Klubbens regnskabsår er 1/7 – 30/6. Perioden 1/1 – 30/6 1995 regnes for et regnskabsår.",
  "Kassereren er ansvarlig for udarbejdelse af regnskabet og budgettet.",
  "Regnskabet skal revideres og godkendes af mindst 1 af de valgte revisorer for at være gyldigt."]),
 ("§ 9. Ophævelse.", [
  "Ophævelse af klubben kan kun ske på en ekstraordinær generalforsamling, som alene er indkaldt med dette formål.",
  "Klubbens virksomhed ophører kun, hvis 2/3 af klubbens medlemmer stemmer herfor.",
  "Ved ophør tilfalder klubbens materialer og midler ungdomsarbejdet i Faaborg-Midtfyn kommune, fortrinsvis til skaklige aktiviteter."]),
]


def build_vedtaegter():
    out = []
    for heading, stks in VEDT:
        out.append(f'  <h2>{heading}</h2>')
        n = 0
        for s in stks:
            n += 1
            if isinstance(s, tuple):
                if s[0] == "__SKIP__":
                    continue          # § 7 springer fra stk. 3 til stk. 5 i originalen
                items = "".join(f"<li>{i}</li>" for i in s[1])
                out.append(f'  <p class="stk"><b>Stk. {n}.</b> {s[0]}</p>\n  <ol>{items}</ol>')
            else:
                out.append(f'  <p class="stk"><b>Stk. {n}.</b> {s}</p>')
    body = page_head("Vedtægter", "Vedtægter for Årslev Skakklub",
        "Stiftet 24. februar 1982. Vedtægterne blev vedtaget på generalforsamlingen "
        "20. februar 1995 og senest ændret 15. september 2025.") + f"""
<section>
  <div class="wrap prose">
{chr(10).join(out)}
  <p class="meta">Ovenstående vedtægter vedtaget på generalforsamlingen d. 20.2.1995 og ændret
     på generalforsamlingen d. 6.9.1999, d. 15.9.2014 samt 15.9.2025.</p>
  </div>
</section>"""
    page("vedtaegter.html", f"Vedtægter – {CLUB}",
         "Vedtægter for Årslev Skakklub, stiftet 24. februar 1982. Senest ændret 15. september 2025.",
         body, active="klubben.html")


# ================================================================ PRIVATLIV
def build_privatliv():
    body = page_head("Privatlivspolitik", "Privatlivspolitik",
        "Version 1 – senest ændret 24. maj 2018. Sådan behandler Årslev Skakklub "
        "dine personoplysninger.") + """
<section>
  <div class="wrap prose">
  <h2>Klubbens dataansvar</h2>
  <p>Vi behandler personoplysninger og bestyrelsen har derfor vedtaget denne privatlivspolitik,
     der kort fortæller dig, hvordan vi behandler dine personoplysninger til sikring af en fair
     og gennemsigtig behandling.</p>
  <p>Gennemgående for vores databehandling er, at vi kun behandler personoplysninger til
     bestemte formål og ud fra berettigede (legitime) interesser. Vi behandler kun
     personoplysninger, der er relevante og nødvendige til opfyldelse af de angivne formål,
     og vi sletter dine oplysninger, når de ikke længere er nødvendige.</p>

  <h2>Kontaktoplysninger på den dataansvarlige</h2>
  <p>Årslev Skakklub er dataansvarlig, og vi sikrer, at dine personoplysninger behandles i
     overensstemmelse med lovgivningen.</p>
  <p>Kontaktperson: Lean Schier (formand)<br>
     Mail: <a href="mailto:lean@schier.dk" style="color:var(--gold)">lean@schier.dk</a></p>

  <h2>Behandling af personoplysninger</h2>
  <p>Vi behandler følgende personoplysninger:</p>
  <h3>1) Medlemsoplysninger</h3>
  <p><em>Almindelige personoplysninger:</em></p>
  <ul>
    <li>Registrerings- og kontaktoplysninger som navn, adresse, indmeldelsesdato,
        telefonnummer, fødselsdato, e-mailadresse</li>
    <li>Turneringsresultater og ratingtal</li>
  </ul>
  <p><em>Personoplysninger, der er tillagt en højere grad af beskyttelse:</em></p>
  <ul>
    <li>CPR-nummer registreres normalt ikke og vil kun blive registreret, hvor dette er et
        krav i henhold til gældende lovgivning</li>
  </ul>
  <h3>2) Oplysninger om ledere og trænere</h3>
  <p><em>Almindelige personoplysninger:</em></p>
  <ul>
    <li>Kontaktoplysninger som navn, adresse, telefonnummer og e-mailadresse</li>
    <li>Oplysninger om tillidsposter og andre hverv i relation til klubben</li>
  </ul>
  <p><em>Personoplysninger, der er tillagt en højere grad af beskyttelse:</em></p>
  <ul>
    <li>CPR-nummer registreres normalt ikke og vil kun blive registreret, hvor dette er et
        krav i henhold til gældende lovgivning</li>
    <li>Oplysninger om strafbare forhold ved indhentelse af børneattest</li>
  </ul>

  <h2>Her indsamler vi oplysninger fra</h2>
  <p>Normalt får vi oplysningerne fra dig. I nogle tilfælde kan der være andre kilder:</p>
  <ul>
    <li>Offentlige myndigheder, f.eks. nødvendige skatteoplysninger ved udbetaling af løn</li>
    <li>Dansk Skak Union og Fyns Skak Union, f.eks. oplysninger om klubskifter,
        kontingentforhold, ratingtal og evt. karantæner</li>
  </ul>

  <h2>Klubbens formål med behandling af dine personoplysninger</h2>
  <p>Vi behandler dine personoplysninger til bestemte formål, når vi har en lovlig grund.
     Lovlige grunde til behandling er særligt:</p>
  <ul>
    <li>Klubbens berettigede (legitime) interesser i at behandle dine oplysninger
        (interesseafvejningsreglen)</li>
    <li>At det er nødvendigt for at opfylde en kontrakt med dig</li>
    <li>Behandling efter lovkrav</li>
    <li>Behandling med samtykke</li>
  </ul>
  <h3>Formål med behandling af medlemsoplysninger</h3>
  <ul>
    <li>Klubbens medlemshåndtering, herunder kontingentopkrævning</li>
    <li>Som led i klubbens skak-aktiviteter og andre aktiviteter, herunder planlægning,
        gennemførelse og opfølgning</li>
    <li>Opfyldelse af lovkrav, herunder folkeoplysningsloven</li>
    <li>Administration af din relation til os</li>
  </ul>
  <h3>Formål med behandling af oplysninger på ledere og trænere</h3>
  <ul>
    <li>Håndtering af trænernes og ledernes hverv og pligter i klubben</li>
    <li>Overblik over og forbedring af erfaringer og kompetencer</li>
    <li>Opfyldelse af lovkrav</li>
    <li>Udbetaling af løn, godtgørelser, refusioner og lignende</li>
    <li>Administration af din relation til os</li>
  </ul>

  <h2>Vi behandler kun personoplysninger ud fra legitime interesser</h2>
  <p>I det omfang vi behandler dine medlemsoplysninger på baggrund af interesseafvejningsreglen,
     vil denne behandling udelukkende være motiveret af berettigede (legitime) interesser som:</p>
  <ul>
    <li>Udøvelse af skak-aktiviteter, herunder udfærdigelse af holdkort, holdopstillinger,
        interne resultatlister m.v.</li>
    <li>Håndtering af dine medlemsrettigheder i henhold til vedtægterne m.v., herunder i
        forhold til generalforsamlingen</li>
    <li>Opfyldelse af medlemspligter, herunder opkrævning og betaling af kontingent m.v.</li>
    <li>Afholdelse af sociale arrangementer, skak-lige aktiviteter samt andre aktiviteter</li>
    <li>Brug af situationsbilleder taget i klubben, der afbilder en konkret aktivitet eller
        situation i klubben</li>
    <li>Videregivelse af dine almindelige personoplysninger til Dansk Skak Union og Fyns Skak
        Union i relevant og nødvendigt omfang i forbindelse med skak-aktiviteter</li>
    <li>Af praktiske og administrative hensyn opbevarer vi dine almindelige medlemsoplysninger
        også i en periode efter din udmeldelse af klubben</li>
    <li>Af hensyn til kontaktmuligheder kan der for børn og unge under 18 år behandles
        oplysninger om forældrene</li>
    <li>Bevaring af oplysninger med historisk værdi til statistik og lignende</li>
  </ul>

  <h2>Samtykke</h2>
  <p>Oftest vil vores behandling af dine personoplysninger basere sig på et andet lovligt
     grundlag end samtykke. Vi indhenter derfor kun dit samtykke, når det i sjældne tilfælde
     er nødvendigt for at behandle dine personoplysninger til de formål, der er beskrevet
     ovenfor.</p>
  <p>Hvis vi indhenter dit samtykke, er det frivilligt, om du vil give samtykke, og du kan
     til enhver tid trække det tilbage ved at give os besked om det.</p>
  <p>Når vi indhenter personoplysninger om børn og unge, foretager vi en vurdering af, om
     barnet selv er i stand til at afgive de pågældende personoplysninger. Hvis ikke,
     indhenter vi samtykke fra en forælder. Vores udgangspunkt er 15 år.</p>
  <p>Indsamler vi personoplysninger på børn via informationstjenester (apps og sociale medier),
     kan børn fra og med de er fyldt 13 år selv afgive samtykke.</p>

  <h2>Videregivelse af dine personoplysninger</h2>
  <ul>
    <li>I forbindelse med skak-aktivitet kan der ske videregivelse af oplysninger om deltagelse
        og resultater til Dansk Skak Union, Fyns Skak Union og til den arrangerende klub</li>
    <li>Der sker videregivelse af oplysninger om ledere og trænere i relevant omfang til
        Dansk Skak Union og Fyns Skak Union</li>
    <li>Vi videregiver ikke personoplysninger til firmaer til markedsføring</li>
  </ul>

  <h2>Opbevaring og sletning af dine personoplysninger</h2>
  <p>Vi har forskellige behandlingsformål og opbevaringsperioder alt efter, om vi behandler
     dine personoplysninger som medlem af klubben, som ulønnet leder eller træner eller som
     lønnet leder eller træner:</p>
  <h3>Medlemmer</h3>
  <ul><li>Af praktiske og administrative hensyn opbevarer vi dine almindelige
      medlemsoplysninger i op til 3 år efter kalenderåret for din udmeldelse af klubben</li></ul>
  <h3>Ulønnede ledere og trænere</h3>
  <ul><li>Af praktiske og administrative hensyn opbevarer vi dine almindelige
      medlemsoplysninger i op til 1 år efter dit virke er ophørt</li></ul>
  <h3>Lønnede ledere og trænere</h3>
  <ul>
    <li>Bogføringsbilag, herunder f.eks. lønbilag, skal gemmes i 5 år fra udløbet af det
        regnskabsår, som bilaget drejer sig om</li>
    <li>Andre relevante oplysninger til opfølgning og stillingtagen til eventuelle krav
        gemmes i 5 år efter arbejdet er ophørt</li>
  </ul>
  <p>Vi opbevarer dog oplysninger på såvel medlemmer, ledere og trænere til statistik og
     lignende, så længe de har historisk værdi.</p>

  <h2>Dine rettigheder</h2>
  <p>Du har en række særlige rettigheder efter persondataforordningen, når vi behandler
     personoplysninger om dig:</p>
  <ul>
    <li>Retten til at blive oplyst om behandlingen af data</li>
    <li>Retten til indsigt i egne personoplysninger</li>
    <li>Retten til berigtigelse</li>
    <li>Retten til sletning</li>
    <li>Retten til begrænsning af behandling</li>
    <li>Retten til dataportabilitet (udlevering af data i et almindeligt anvendt format)</li>
    <li>Retten til indsigelse</li>
  </ul>
  <p>Du kan gøre brug af dine rettigheder, herunder gøre indsigelse mod vores behandling, ved
     at henvende dig til os. Vores kontaktoplysninger finder du øverst.</p>
  <p>Hvis du f.eks. henvender dig med en anmodning om at få rettet eller slettet dine
     personoplysninger, undersøger vi, om betingelserne er opfyldt, og gennemfører i så fald
     ændringer eller sletning så hurtigt som muligt.</p>
  <p>Du kan altid indgive en klage til en databeskyttelsestilsynsmyndighed, f.eks. Datatilsynet.</p>

  <h2>Revidering af privatlivspolitikken</h2>
  <p>Vi forbeholder os retten til at foretage ændringer i denne privatlivspolitik fra tid til
     anden. Ved ændringer vil datoen øverst i privatlivspolitikken blive ændret. Den til enhver
     tid gældende privatlivspolitik vil være tilgængelig på vores websted. Ved væsentlige
     ændringer vil du modtage meddelelse herom.</p>
  <p class="meta">Version 1 – senest ændret 24/5-2018.</p>
  </div>
</section>"""
    page("privatlivspolitik.html", f"Privatlivspolitik – {CLUB}",
         "Sådan behandler Årslev Skakklub personoplysninger. Version 1, senest ændret 24. maj 2018.",
         body, active="info.html")


# ================================================================ EKSTRA FILER
def build_extras():
    pages = [u for u, _ in NAV] + ["vedtaegter.html", "privatlivspolitik.html"]
    urls = "\n".join(
        f"  <url><loc>{SITE}/{'' if p == 'index.html' else p}</loc>"
        f"<lastmod>{BUILT}</lastmod>"
        f"<priority>{'1.0' if p == 'index.html' else '0.7'}</priority></url>" for p in pages)
    pathlib.Path("sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n',
        encoding="utf-8")
    pathlib.Path("robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")

    ev = ",\n".join('  {d:"%s",t:"%s",k:"%s"}' % (iso, akt.replace('"', ''), typ)
                    for _, iso, akt, typ in CAL_AUTUMN if typ != "fri")
    pathlib.Path("assets/js/events.js").write_text(
        "/* Genereret af build.py - ret kalenderen i build.py, ikke her. */\n"
        "window.AARSLEV_EVENTS = [\n" + ev + "\n];\n", encoding="utf-8")
    print("  → sitemap.xml, robots.txt, assets/js/events.js")


if __name__ == "__main__":
    print(f"Bygger {CLUB} …")
    build_index()
    build_nyheder()
    build_kalender()
    build_turneringer()
    build_klubben()
    build_info()
    build_vedtaegter()
    build_privatliv()
    build_extras()
    print("Færdig.")
