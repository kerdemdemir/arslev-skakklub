# Årslev Skakklub — hjemmeside

Statisk hjemmeside for [Årslev Skakklub](https://www.arslevskak.duckdns.org),
en skakklub i Faaborg-Midtfyn Kommune på Fyn, stiftet 1982.

Alt indhold er overført fra klubbens tidligere Wix-side.

## Indhold

| Fil | Side |
|---|---|
| `index.html` | Forside |
| `nyheder.html` | Nyheder |
| `kalender.html` | Sæsonkalender 2026/2027 |
| `turneringer.html` | Turneringer og rundeskema |
| `klubben.html` | Om klubben, bestyrelse, traditioner |
| `info.html` | Praktisk info, kontakt, bliv medlem |
| `vedtaegter.html` | Vedtægter |
| `privatlivspolitik.html` | Privatlivspolitik |

Ingen build-tools, ingen frameworks, ingen cookies eller sporing.
Kun HTML, CSS og ~100 linjer JavaScript.

## Sådan retter du indholdet

HTML-filerne er **genereret**. Ret ikke i dem direkte — ret i `build.py`
og kør derefter:

```bash
python3 build.py
```

De vigtigste steder i `build.py`:

- `CAL_AUTUMN` — sæsonkalenderen (uge, dato, aktivitet, type)
- `NEWS` — nyheder (nyeste først)
- `BOARD` — bestyrelsens navne, telefon og mail
- `VENUE` — spillestedets adresse
- `PLAYERS` / `BERGER` — deltagere og rundeskema i klubturneringen

Kalenderen genererer også `assets/js/events.js`, som driver
„Næste klubaften“-feltet og markeringen af afviklede runder.

## Udrulning

```bash
./deploy.sh
```

Scriptet kører `build.py`, synkroniserer filerne til serveren med `rsync`
og genindlæser nginx. Serveren er en Ubuntu-maskine med nginx;
webroden er `/var/www/arslevskak`.

Nginx-konfigurationen ligger i `nginx/arslevskak.conf`.
TLS-certifikatet udstedes af Let's Encrypt via certbot og fornys automatisk.

## Licens

Indhold og logo © Årslev Skakklub. Kode må frit genbruges.
