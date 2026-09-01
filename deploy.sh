#!/usr/bin/env bash
# Bygger og udruller hjemmesiden til serveren.
set -euo pipefail

SERVER="${ARSLEV_SERVER:-root@204.168.138.132}"
WEBROOT="/var/www/arslevskak"

cd "$(dirname "$0")"

echo "→ Bygger siden …"
python3 build.py

echo "→ Synkroniserer til $SERVER:$WEBROOT …"
rsync -az --delete \
  --exclude '.git' --exclude '.gitignore' --exclude 'build.py' \
  --exclude 'deploy.sh' --exclude 'README.md' --exclude 'nginx' \
  --exclude '__pycache__' \
  ./ "$SERVER:$WEBROOT/"

echo "→ Genindlæser nginx …"
ssh "$SERVER" 'nginx -t && systemctl reload nginx'

echo "✓ Udrullet: https://www.arslevskak.duckdns.org"
