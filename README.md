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

Bag login ligger desuden `/admin` (nyheder og billeder) og `/admin/partier`
(partiarkiv med bræt og motor). De er ikke en del af den offentlige side.

Ingen build-tools, ingen frameworks, ingen cookies eller sporing.
Kun HTML, CSS og ~100 linjer JavaScript.

## Nyheder: admin-siden

Nyheder og billeder lægges ud via **<https://www.arslevskak.duckdns.org/admin>**.
Log ind, skriv nyheden, læg eventuelt billeder på — siden bliver bygget og
opdateret med det samme.

Bemærk hvordan det hænger sammen: den offentlige side er stadig **rene
statiske filer**. Admin-siden retter i `content/news.json`, kører `build.py`
og kopierer resultatet til webroden. Besøgende rammer aldrig et program, og
går admin-siden ned, står hjemmesiden uberørt.

Praktisk om admin-siden:

- Én tom linje i teksten bliver et nyt afsnit. Der skal ikke bruges HTML.
- Billeder bliver gen-kodet med Pillow. Det skalerer dem ned til højst
  2000 px og fjerner samtidig EXIF-data — altså også kameraets GPS-position.
- Sletter man en nyhed, bliver dens billedfiler slettet med.
- Adgangskoden ligger som et bcrypt-hash i `/etc/arslevskak/admin.env`
  på serveren (kun læsbar for root). Den står **ikke** i dette repo.

For at skifte adgangskode:

```bash
# på serveren
python3 -c "import bcrypt,getpass; print(bcrypt.hashpw(getpass.getpass().encode(), bcrypt.gensalt(12)).decode())"
# indsæt resultatet som ARSLEV_ADMIN_HASH i /etc/arslevskak/admin.env
systemctl restart arslevskak-admin
```

## Partiarkivet (kun for administratorer)

**<https://www.arslevskak.duckdns.org/admin/partier>** — importér PGN-filer og
gennemgå partierne med bræt og motor.

Siden ligger bag login og bliver **aldrig** bygget ind i den offentlige
hjemmeside. Partierne gemmes i `content/games/`, som ikke kopieres til
webroden.

- En PGN-fil kan indeholde flere partier; de bliver alle læst ind.
- Den oprindelige PGN gemmes uændret og kan hentes igen med „Hent PGN“,
  så importen ikke kan koste data.
- Piletasterne bladrer gennem partiet. „⇅ Vend“ vender brættet.
- **Motor: til** vurderer den aktuelle stilling.
  **Gennemgå hele partiet** vurderer alle stillinger og markerer derefter
  unøjagtigheder, fejl og bommerter i tekstlisten.

Al skak-logik ligger på serveren i `admin/pgn.py`, som læser PGN'en med
`python-chess` og gemmer en færdig liste af stillinger (FEN). Browseren
skal derfor ikke kunne skakreglerne — `admin/static/viewer.js` tegner bare
et bræt ud fra en FEN.

Motoren er Stockfish 18 Lite (enkelttrådet), som kører i browseren.
Mønsteret er taget fra `VisionChessVAR`: de ~21 KB worker-kode udleveres fra
vores egen server (`admin/static/sf/`), mens selve wasm-filen på ~7 MB hentes
fra jsDelivr — se `WASM` i `viewer.js`, hvis den skal hostes lokalt i stedet.
Den enkelttrådede udgave kræver ingen `SharedArrayBuffer` og dermed heller
ingen særlige cross-origin-headere.

## Sådan retter du det øvrige indhold

HTML-filerne er **genereret**. Ret ikke i dem direkte — ret i `build.py`
og kør derefter:

```bash
python3 build.py
```

De vigtigste steder i `build.py`:

- `CAL_AUTUMN` — sæsonkalenderen (uge, dato, aktivitet, type)
- `BOARD` — bestyrelsens navne, telefon og mail
- `VENUE` — spillestedets adresse
- `PLAYERS` / `BERGER` — deltagere og rundeskema i klubturneringen

Nyheder ligger derimod i `content/news.json` og redigeres normalt via
admin-siden.

Kalenderen genererer også `assets/js/events.js`, som driver
„Næste klubaften“-feltet og markeringen af afviklede runder.

## Udrulning

```bash
./deploy.sh        # send kode op, byg på serveren, genstart admin, reload nginx
./fetch-content.sh # hent nyheder og billeder ned fra serveren igen
```

`deploy.sh` sender **kildekoden** til `/srv/arslevskak` på serveren og kører
`publish.sh` der, som bygger siden og kopierer de offentlige filer til
webroden `/var/www/arslevskak`.

`content/` og `assets/img/nyheder/` bliver med vilje ikke sendt op — de
tilhører serveren, fordi administratorerne redigerer dem via `/admin`. Kør
`fetch-content.sh` for at hente dem ned, inden du committer.

| Del | Sti |
|---|---|
| Kildekode på serveren | `/srv/arslevskak` |
| Webrod (offentlig) | `/var/www/arslevskak` |
| Admin-app | `admin/app.py`, uvicorn på 127.0.0.1:8096 |
| systemd-unit | `systemd/arslevskak-admin.service` |
| Hemmeligheder | `/etc/arslevskak/admin.env` (root, 0600) |
| nginx | `nginx/arslevskak.conf` |

Appen kører som brugeren `arslev` og må kun skrive i `/srv/arslevskak` og
`/var/www/arslevskak` (se `ReadWritePaths` i unit-filen).
TLS-certifikatet udstedes af Let's Encrypt via certbot og fornys automatisk.

## Licens

Indhold og logo © Årslev Skakklub. Kode må frit genbruges.
