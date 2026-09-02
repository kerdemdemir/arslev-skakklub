#!/usr/bin/env bash
# Henter nyheder, partier og billeder ned fra serveren, så repoet er ajour med
# det, administratorerne har lagt ud via /admin. Kør den inden du committer.
set -euo pipefail

SERVER="${ARSLEV_SERVER:-root@204.168.138.132}"
cd "$(dirname "$0")"

mkdir -p content assets/img/nyheder
rsync -az "$SERVER:/srv/arslevskak/content/" ./content/
rsync -az "$SERVER:/srv/arslevskak/assets/img/nyheder/" ./assets/img/nyheder/

echo "✓ Hentet. Kør 'git status' for at se, hvad der er nyt."
