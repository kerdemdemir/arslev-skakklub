#!/usr/bin/env bash
# Udruller kildekoden til serveren, bygger siden der og genindlæser nginx.
#
# content/ og assets/img/nyheder/ hører til SERVEREN - de redigeres via /admin
# og bliver derfor aldrig overskrevet herfra. Brug fetch-content.sh for at
# hente dem ned i repoet, inden du committer.
set -euo pipefail

SERVER="${ARSLEV_SERVER:-root@204.168.138.132}"
SRCDIR="/srv/arslevskak"

cd "$(dirname "$0")"

echo "→ Synkroniserer kildekoden til $SERVER:$SRCDIR …"
rsync -az --delete \
  --exclude '.git' --exclude '__pycache__' --exclude 'venv' \
  --exclude 'content/' --exclude 'assets/img/nyheder/' \
  ./ "$SERVER:$SRCDIR/"

echo "→ Bygger og publicerer på serveren …"
ssh "$SERVER" "cd $SRCDIR && ./publish.sh"

echo "→ Retter ejerskab, genstarter admin-siden og genindlæser nginx …"
ssh "$SERVER" 'chown -R arslev:www-data /srv/arslevskak /var/www/arslevskak
               systemctl restart arslevskak-admin
               nginx -t && systemctl reload nginx'

echo "✓ Udrullet: https://aarslevskak.com"
