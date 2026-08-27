#!/usr/bin/env bash
#
# psi-attente.sh — Attend la réinitialisation du quota PageSpeed Insights,
# puis récupère le rapport du site (mobile et ordinateur).
#
# Le quota anonyme de l'API PageSpeed est journalier et censé se réinitialiser
# à minuit heure du Pacifique, soit 07h00 UTC. Ce script attend cette heure,
# puis réessaie régulièrement jusqu'à obtenir un rapport.
#
# ATTENTION : sans clé, l'appel est compté sur un quota partagé entre tous les
# appelants anonymes de la même infrastructure. Constaté le 2026-08-27 depuis
# l'environnement Claude Code distant : quota saturé en permanence, y compris
# plus de trois heures après l'heure de réinitialisation. Ce script n'a donc
# d'intérêt qu'avec une clé :
#
#   export PSI_API_KEY=...   (clé gratuite, console Google Cloud,
#                             API "PageSpeed Insights" à activer)
#
# Usage : ./scripts/psi-attente.sh [url] [dossier_sortie]

set -uo pipefail

SITE="${1:-https://njaho.com}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOMAIN="$(printf '%s' "$SITE" | sed -E 's#^https?://##; s#/.*##')"
OUT="${2:-$ROOT/reports/site-audit-$DOMAIN-$(date +%Y-%m-%d)}"
LOG="$OUT/psi-attente.log"

mkdir -p "$OUT/raw"

journal() { printf '[%s] %s\n' "$(date -u +%H:%M:%S)" "$*" >> "$LOG"; }

if [ -z "${PSI_API_KEY:-}" ]; then
  journal "Aucune PSI_API_KEY : appels sur le quota anonyme partagé, souvent saturé."
  echo "Avertissement : PSI_API_KEY non définie. Le quota anonyme est partagé et" >&2
  echo "souvent indisponible. Voir l'en-tête du script pour obtenir une clé." >&2
fi

# --- Attente jusqu'à 07h05 UTC (quota réinitialisé à 07h00 UTC) -------------
CIBLE=$(date -u -d "today 07:05" +%s 2>/dev/null || echo 0)
MAINTENANT=$(date -u +%s)
if [ "$CIBLE" -gt 0 ] && [ "$MAINTENANT" -lt "$CIBLE" ]; then
  ATTENTE=$((CIBLE - MAINTENANT))
  journal "Attente de $((ATTENTE / 60)) min jusqu'à la réinitialisation du quota."
  sleep "$ATTENTE"
fi

psi_url() {
  local u
  u="$(printf 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=%s&strategy=%s&category=performance&category=seo&category=accessibility&category=best-practices' \
    "$SITE" "$1")"
  # Sans clé, l'appel passe par le quota anonyme, partagé entre tous les
  # appelants et souvent saturé toute la journée. Une clé gratuite le règle.
  [ -n "${PSI_API_KEY:-}" ] && u="$u&key=$PSI_API_KEY"
  printf '%s' "$u"
}

recupere() { # recupere <strategie> <fichier> -> 0 si rapport valide
  curl -sS --max-time 150 "$(psi_url "$1")" -o "$2" 2>>"$LOG"
  python3 - "$2" <<'PY' >> "$LOG" 2>&1
import json, sys
try:
    d = json.load(open(sys.argv[1], encoding='utf-8'))
except Exception as e:
    print("JSON illisible :", e); raise SystemExit(2)
if 'error' in d:
    print("erreur API :", d['error'].get('code'), d['error'].get('message', '')[:90])
    raise SystemExit(1)
score = d.get('lighthouseResult', {}).get('categories', {}).get('performance', {}).get('score')
print("rapport valide, score performance :", score)
PY
}

# --- Tentatives : 12 essais espacés de 15 min, soit 3 h de fenêtre ----------
for essai in $(seq 1 12); do
  journal "Tentative $essai (mobile)"
  if recupere mobile "$OUT/raw/psi-mobile.json"; then
    journal "Rapport mobile obtenu."
    sleep 5
    if recupere desktop "$OUT/raw/psi-desktop.json"; then
      journal "Rapport ordinateur obtenu."
    else
      journal "Rapport ordinateur indisponible, on continue avec le mobile seul."
      rm -f "$OUT/raw/psi-desktop.json"
    fi

    ARGS=("$OUT/raw/psi-mobile.json")
    [ -s "$OUT/raw/psi-desktop.json" ] && ARGS+=("$OUT/raw/psi-desktop.json")
    if python3 "$ROOT/scripts/psi-analyse.py" "${ARGS[@]}" > "$OUT/PAGESPEED.md" 2>>"$LOG"; then
      journal "Analyse écrite dans $OUT/PAGESPEED.md"
      echo "SUCCES: $OUT/PAGESPEED.md"
      exit 0
    fi
    journal "Analyse en échec, voir le journal."
    exit 3
  fi
  journal "Quota encore épuisé, nouvelle tentative dans 15 min."
  sleep 900
done

journal "Abandon après 12 tentatives."
echo "ECHEC: quota PageSpeed toujours indisponible après 12 tentatives, voir $LOG"
exit 1
