#!/usr/bin/env bash
# Flytter siden til aarslevskak.com.
#
# Kør den FØRST når DNS hos Porkbun peger på serveren:
#   aarslevskak.com      A      204.168.138.132
#   www.aarslevskak.com  CNAME  aarslevskak.com   (eller samme A-record)
#
# Scriptet henter certifikat, lægger den nye nginx-konfiguration ind og
# bygger siden med den nye adresse. Den gamle duckdns-adresse bliver
# omdirigeret, så gamle links stadig virker.
set -euo pipefail

SERVER="${ARSLEV_SERVER:-root@204.168.138.132}"
IP="${ARSLEV_IP:-204.168.138.132}"
DOMAIN=aarslevskak.com

cd "$(dirname "$0")/.."

echo "→ Kontrollerer DNS …"
for name in "$DOMAIN" "www.$DOMAIN"; do
    got=$(dig +short A "$name" @1.1.1.1 | grep -E '^[0-9.]+$' | head -1 || true)
    if [ "$got" != "$IP" ]; then
        echo "✗ $name peger på '${got:-ingenting}', ikke på $IP."
        echo "  Ret DNS hos Porkbun først, og vent til ændringen er slået igennem."
        exit 1
    fi
    echo "  ✓ $name → $IP"
done

echo "→ Henter certifikat til $DOMAIN …"
ssh "$SERVER" "certbot certonly --webroot -w /var/www/arslevskak \
    -d $DOMAIN -d www.$DOMAIN \
    --non-interactive --agree-tos --keep-until-expiring"

echo "→ Lægger nginx-konfigurationen ind …"
scp nginx/arslevskak.conf "$SERVER:/etc/nginx/sites-available/arslevskak"
# Den midlertidige ACME-vhost skal væk, ellers strides den med den rigtige
# konfiguration om samme server_name på port 80.
ssh "$SERVER" 'rm -f /etc/nginx/sites-enabled/aarslevskak-acme \
                     /etc/nginx/sites-available/aarslevskak-acme
               nginx -t && systemctl reload nginx'

echo "→ Bygger siden med den nye adresse …"
./deploy.sh

echo
echo "✓ Færdig. Kontrollér:"
echo "    https://$DOMAIN"
echo "    https://www.$DOMAIN            (skal give 301)"
echo "    https://www.arslevskak.duckdns.org  (skal give 301)"
