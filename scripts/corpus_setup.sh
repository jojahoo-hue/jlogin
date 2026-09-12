#!/bin/bash
# Enchaîne les étapes de mise en place du corpus, dans l'ordre sûr.
# La sauvegarde locale passe toujours avant toute écriture dans Notion.
#
#   bash scripts/corpus_setup.sh            # rapports seuls, rien n'est modifié
#   bash scripts/corpus_setup.sh --apply    # applique les changements Notion

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

APPLY=""
[ "${1:-}" = "--apply" ] && APPLY="--apply"

if [ ! -f .env ]; then
  echo "Fichier .env absent. Crée-le à la racine avec :"
  echo "  NOTION_TOKEN=ntn_xxxxxxxx"
  echo "Token à créer sur https://www.notion.so/my-integrations"
  echo "puis connecter l'intégration aux bases Plaud Archive et Manuscrits."
  exit 1
fi

python3 -c "import yaml" 2>/dev/null || { echo "pip3 install pyyaml"; exit 1; }

echo "=== 1/3  Export du corpus depuis Notion ==="
python3 scripts/corpus_export.py

echo
echo "=== 2/3  Taxonomie ==="
python3 scripts/notion_taxonomie.py $APPLY

echo
echo "=== 3/3  Manuscrits : doublons et numérotation ==="
python3 scripts/manuscrits_dedup.py $APPLY

echo
if [ -z "$APPLY" ]; then
  echo "Rapports produits, rien n'a été modifié dans Notion."
  echo "Relis reports/manuscrits-doublons.md puis relance avec --apply."
else
  echo "Terminé. Étapes suivantes dans Claude Code :"
  echo "  /corpus listing"
  echo "  /corpus rattrapage"
  echo "  /manuscrit \"Nza Nga dia KiTuni\" plan"
fi
