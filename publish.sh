#!/usr/bin/env bash
# Bygger de statiske sider og kopierer dem til webroden.
# Bruges både af deploy.sh (fra en pc) og af admin-siden på serveren.
set -euo pipefail
cd "$(dirname "$0")"

WEBROOT="${ARSLEV_WEBROOT:-/var/www/arslevskak}"

python3 build.py

# Kun de offentlige filer kopieres. build.py, content/, admin/ m.v. bliver
# liggende i kildemappen og kommer aldrig ud på nettet.
rsync -a --delete \
  --filter='+ /assets/***' \
  --filter='+ /*.html' \
  --filter='+ /robots.txt' \
  --filter='+ /sitemap.xml' \
  --filter='- *' \
  ./ "$WEBROOT/"

echo "publiceret til $WEBROOT"
