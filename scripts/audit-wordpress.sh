#!/usr/bin/env bash
#
# audit-wordpress.sh — Collecte automatique des données d'un site WordPress
#
# Usage :
#   ./scripts/audit-wordpress.sh                  # audite https://njaho.com
#   ./scripts/audit-wordpress.sh https://mon-site.com
#
# Ce script ne modifie RIEN sur le site. Il ne fait que lire des pages publiques.
# Résultat écrit dans reports/site-audit-<domaine>-<date>/
#
# Prérequis : curl. Optionnels : python3 (analyse HTML fine), jq (PageSpeed).
# PageSpeed Insights : export PSI_API_KEY=... pour éviter le quota anonyme.

set -uo pipefail

SITE="${1:-https://njaho.com}"
SITE="${SITE%/}"
DOMAIN="$(printf '%s' "$SITE" | sed -E 's#^https?://##; s#/.*##')"
DATE="$(date +%Y-%m-%d)"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/reports/site-audit-$DOMAIN-$DATE"
UA="Mozilla/5.0 (compatible; JarvisAudit/1.0; +audit interne)"

mkdir -p "$OUT/raw"

say()  { printf '\n\033[1m%s\033[0m\n' "$*"; }
ok()   { printf '  [OK]   %s\n' "$*"; }
warn() { printf '  [!]    %s\n' "$*"; }
info() { printf '  ...    %s\n' "$*"; }

fetch() { # fetch <url> <fichier_sortie> -> code HTTP sur stdout
  curl -sS -L --max-time 30 -A "$UA" -o "$2" -w '%{http_code}' "$1" 2>/dev/null || echo "000"
}

say "Audit de $SITE  ->  $OUT"

# ---------------------------------------------------------------------------
# 1. Accueil : disponibilité, temps de réponse, poids
# ---------------------------------------------------------------------------
say "1. Disponibilité et temps de réponse"

curl -sS -L --max-time 30 -A "$UA" \
  -o "$OUT/raw/home.html" \
  -D "$OUT/raw/home-headers.txt" \
  -w 'http_code=%{http_code}\ntime_namelookup=%{time_namelookup}\ntime_connect=%{time_connect}\ntime_appconnect=%{time_appconnect}\nttfb=%{time_starttransfer}\ntime_total=%{time_total}\nsize_download=%{size_download}\nredirects=%{num_redirects}\nurl_final=%{url_effective}\n' \
  "$SITE/" > "$OUT/raw/home-timing.txt" 2>/dev/null

if [ ! -s "$OUT/raw/home.html" ]; then
  warn "Impossible de récupérer $SITE/ — vérifie le domaine ou ta connexion."
  cat "$OUT/raw/home-timing.txt" 2>/dev/null
  exit 1
fi

TTFB=$(grep '^ttfb=' "$OUT/raw/home-timing.txt" | cut -d= -f2)
TOTAL=$(grep '^time_total=' "$OUT/raw/home-timing.txt" | cut -d= -f2)
SIZE=$(grep '^size_download=' "$OUT/raw/home-timing.txt" | cut -d= -f2)
CODE=$(grep '^http_code=' "$OUT/raw/home-timing.txt" | cut -d= -f2)
ok "HTTP $CODE — TTFB ${TTFB}s — total ${TOTAL}s — HTML $((SIZE / 1024)) Ko"

# ---------------------------------------------------------------------------
# 2. Empreinte WordPress : thème, plugins, version, constructeur de page
# ---------------------------------------------------------------------------
say "2. Empreinte WordPress"

grep -oE 'wp-content/themes/[^/"'"'"']+' "$OUT/raw/home.html" \
  | sed 's#.*/##' | sort -u > "$OUT/raw/themes.txt"
grep -oE 'wp-content/plugins/[^/"'"'"']+' "$OUT/raw/home.html" \
  | sed 's#.*/##' | sort -u > "$OUT/raw/plugins.txt"
grep -oiE '<meta name="generator" content="[^"]+"' "$OUT/raw/home.html" \
  > "$OUT/raw/generator.txt" 2>/dev/null

info "Thème(s) détecté(s) : $(tr '\n' ' ' < "$OUT/raw/themes.txt")"
info "Plugins visibles côté public : $(wc -l < "$OUT/raw/plugins.txt")"
sed 's/^/         - /' "$OUT/raw/plugins.txt"

# Constructeur de page
BUILDER="aucun détecté (probablement éditeur de blocs Gutenberg)"
grep -qi 'elementor'      "$OUT/raw/home.html" && BUILDER="Elementor"
grep -qi 'wpbakery\|js_composer' "$OUT/raw/home.html" && BUILDER="WPBakery"
grep -qi 'fusion-builder' "$OUT/raw/home.html" && BUILDER="Avada Fusion Builder"
grep -qi 'et_pb_'         "$OUT/raw/home.html" && BUILDER="Divi Builder"
grep -qi 'brxe-\|bricks/' "$OUT/raw/home.html" && BUILDER="Bricks"
info "Constructeur de page : $BUILDER"

# ---------------------------------------------------------------------------
# 3. Surface de sécurité (lecture seule, aucune intrusion)
# ---------------------------------------------------------------------------
say "3. Surface de sécurité"

for path in readme.html license.txt xmlrpc.php wp-login.php wp-cron.php \
            "wp-json/wp/v2/users" "?author=1" "wp-content/debug.log" \
            ".env" "wp-config.php.bak" "wp-config.php.save"; do
  slug=$(printf '%s' "$path" | tr -c 'A-Za-z0-9._-' '_')
  code=$(fetch "$SITE/$path" "$OUT/raw/probe-$slug.txt")
  case "$path:$code" in
    *:200)
      case "$path" in
        wp-login.php|wp-cron.php) info "$path -> 200 (normal)" ;;
        *) warn "$path -> 200 EXPOSÉ, à fermer" ;;
      esac ;;
    *) info "$path -> $code" ;;
  esac
done

say "   En-têtes de sécurité"
for h in strict-transport-security content-security-policy x-frame-options \
         x-content-type-options referrer-policy permissions-policy; do
  if grep -qi "^$h:" "$OUT/raw/home-headers.txt"; then
    ok "$h présent"
  else
    warn "$h ABSENT"
  fi
done
grep -qi '^server:' "$OUT/raw/home-headers.txt" && \
  info "$(grep -i '^server:' "$OUT/raw/home-headers.txt" | head -1 | tr -d '\r')"

# Cache serveur (LiteSpeed sur Hostinger, Cloudflare, etc.)
say "   Cache et CDN"
for h in x-litespeed-cache x-cache cf-cache-status x-hostinger-cache age; do
  grep -qi "^$h:" "$OUT/raw/home-headers.txt" && \
    ok "$(grep -i "^$h:" "$OUT/raw/home-headers.txt" | head -1 | tr -d '\r')"
done
grep -qiE '^(x-litespeed-cache|x-cache|cf-cache-status|x-hostinger-cache):' \
  "$OUT/raw/home-headers.txt" || warn "aucun en-tête de cache détecté, page servie sans cache"

# ---------------------------------------------------------------------------
# 4. SEO : robots, sitemap, balises, structure des titres
# ---------------------------------------------------------------------------
say "4. SEO"

fetch "$SITE/robots.txt" "$OUT/raw/robots.txt" >/dev/null
grep -qi 'disallow: /$' "$OUT/raw/robots.txt" 2>/dev/null && \
  warn "robots.txt bloque tout le site" || ok "robots.txt sans blocage global"

SITEMAP=""
for s in wp-sitemap.xml sitemap_index.xml sitemap.xml; do
  code=$(fetch "$SITE/$s" "$OUT/raw/$s")
  [ "$code" = "200" ] && { SITEMAP="$s"; ok "sitemap trouvé : /$s"; break; }
done
[ -z "$SITEMAP" ] && warn "aucun sitemap XML trouvé"

if command -v python3 >/dev/null 2>&1; then
  python3 - "$OUT/raw/home.html" > "$OUT/raw/seo.txt" <<'PY'
import re, sys, html
src = open(sys.argv[1], encoding='utf-8', errors='replace').read()

def first(pat):
    m = re.search(pat, src, re.I | re.S)
    return html.unescape(m.group(1).strip()) if m else None

title = first(r'<title[^>]*>(.*?)</title>')
desc  = first(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']')
og    = first(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\'](.*?)["\']')
lang  = first(r'<html[^>]+lang=["\']([^"\']+)')
canon = first(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\'](.*?)["\']')

print(f"lang           : {lang or 'ABSENT'}")
print(f"title ({len(title) if title else 0} car.) : {title or 'ABSENT'}")
print(f"meta description ({len(desc) if desc else 0} car.) : {desc or 'ABSENTE'}")
print(f"canonical      : {canon or 'ABSENT'}")
print(f"og:image       : {og or 'ABSENT (mauvais rendu au partage)'}")

for n in (1, 2, 3):
    hs = [re.sub(r'<[^>]+>', '', h).strip()
          for h in re.findall(rf'<h{n}[^>]*>(.*?)</h{n}>', src, re.I | re.S)]
    print(f"H{n} x{len(hs)}       : {' | '.join(hs)[:200]}")

imgs = re.findall(r'<img\b[^>]*>', src, re.I)
noalt = [i for i in imgs if not re.search(r'\balt\s*=\s*["\'][^"\']+', i, re.I)]
lazy  = [i for i in imgs if re.search(r'loading\s*=\s*["\']lazy', i, re.I)]
print(f"images         : {len(imgs)} dont {len(noalt)} sans alt, {len(lazy)} en lazy-load")

print(f"scripts        : {len(re.findall(r'<script\\b[^>]*src=', src, re.I))} fichiers JS externes")
print(f"styles         : {len(re.findall(r'<link\\b[^>]*stylesheet', src, re.I))} feuilles CSS")

fonts = set(re.findall(r'https?://fonts\.(?:googleapis|gstatic)\.com', src, re.I))
if fonts:
    print("polices        : Google Fonts chargées à distance (RGPD + perf : à héberger localement)")
PY
  cat "$OUT/raw/seo.txt"
else
  warn "python3 absent, analyse SEO fine ignorée"
fi

# ---------------------------------------------------------------------------
# 5. Poids réel des ressources (les 15 plus lourdes)
# ---------------------------------------------------------------------------
say "5. Ressources les plus lourdes"

grep -oE 'https?://[^"'"'"' ]+\.(jpg|jpeg|png|gif|webp|avif|svg|css|js|woff2?|mp4)' \
  "$OUT/raw/home.html" | sort -u | head -80 > "$OUT/raw/assets.txt"

: > "$OUT/raw/assets-size.txt"
while read -r url; do
  [ -z "$url" ] && continue
  bytes=$(curl -sSI -L --max-time 15 -A "$UA" "$url" 2>/dev/null \
          | grep -i '^content-length:' | tail -1 | tr -dc '0-9')
  [ -n "$bytes" ] && printf '%s\t%s\n' "$bytes" "$url" >> "$OUT/raw/assets-size.txt"
done < "$OUT/raw/assets.txt"

if [ -s "$OUT/raw/assets-size.txt" ]; then
  TOTAL_BYTES=$(awk -F'\t' '{s+=$1} END {print s+0}' "$OUT/raw/assets-size.txt")
  info "Poids cumulé des ressources analysées : $((TOTAL_BYTES / 1024)) Ko"
  sort -rn "$OUT/raw/assets-size.txt" | head -15 \
    | awk -F'\t' '{printf "         %6d Ko  %s\n", $1/1024, $2}'
  awk -F'\t' '$1 > 300000 {c++} END {if (c) printf "  [!]    %d ressource(s) de plus de 300 Ko\n", c}' \
    "$OUT/raw/assets-size.txt"
fi

# ---------------------------------------------------------------------------
# 6. PageSpeed Insights (Core Web Vitals réels + score Lighthouse)
# ---------------------------------------------------------------------------
say "6. PageSpeed Insights"

psi_url() { # psi_url <strategy>
  local u="https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=$SITE&strategy=$1&category=performance&category=seo&category=accessibility&category=best-practices"
  [ -n "${PSI_API_KEY:-}" ] && u="$u&key=$PSI_API_KEY"
  printf '%s' "$u"
}

curl -sS --max-time 120 "$(psi_url desktop)" -o "$OUT/raw/psi-desktop.json" 2>/dev/null &
PSI_DESKTOP_PID=$!

if curl -sS --max-time 120 "$(psi_url mobile)" -o "$OUT/raw/psi-mobile.json" 2>/dev/null \
   && [ -s "$OUT/raw/psi-mobile.json" ]; then
  wait "$PSI_DESKTOP_PID" 2>/dev/null

  # Analyse détaillée si l'analyseur dédié est disponible
  if command -v python3 >/dev/null 2>&1 && [ -f "$ROOT/scripts/psi-analyse.py" ]; then
    ARGS=("$OUT/raw/psi-mobile.json")
    [ -s "$OUT/raw/psi-desktop.json" ] && ARGS+=("$OUT/raw/psi-desktop.json")
    if python3 "$ROOT/scripts/psi-analyse.py" "${ARGS[@]}" > "$OUT/PAGESPEED.md" 2>&1; then
      ok "analyse détaillée : $OUT/PAGESPEED.md"
      sed -n '1,60p' "$OUT/PAGESPEED.md" | sed 's/^/  /'
    else
      warn "$(head -2 "$OUT/PAGESPEED.md")"
    fi
  fi

else
  warn "PageSpeed injoignable (quota anonyme ?). Réessaie avec PSI_API_KEY."
fi

# ---------------------------------------------------------------------------
# 7. Pages du site (via sitemap)
# ---------------------------------------------------------------------------
if [ -n "$SITEMAP" ]; then
  say "7. Pages listées dans le sitemap"
  grep -oE '<loc>[^<]+</loc>' "$OUT/raw/$SITEMAP" \
    | sed 's#</\?loc>##g' > "$OUT/raw/urls.txt"
  # sitemap index : suivre les sous-sitemaps
  if grep -qi 'sitemapindex' "$OUT/raw/$SITEMAP"; then
    : > "$OUT/raw/urls.txt"
    while read -r sub; do
      curl -sS -L --max-time 20 -A "$UA" "$sub" 2>/dev/null \
        | grep -oE '<loc>[^<]+</loc>' | sed 's#</\?loc>##g' >> "$OUT/raw/urls.txt"
    done < <(grep -oE '<loc>[^<]+</loc>' "$OUT/raw/$SITEMAP" | sed 's#</\?loc>##g')
  fi
  sort -u -o "$OUT/raw/urls.txt" "$OUT/raw/urls.txt"
  info "$(wc -l < "$OUT/raw/urls.txt") URL(s) publiées"
  head -40 "$OUT/raw/urls.txt" | sed 's/^/         /'
fi

# ---------------------------------------------------------------------------
# Synthèse
# ---------------------------------------------------------------------------
{
  echo "# Audit technique — $DOMAIN"
  echo
  echo "Date : $DATE"
  echo "URL auditée : $SITE"
  echo
  echo "## Réponse serveur"
  echo '```'
  cat "$OUT/raw/home-timing.txt"
  echo '```'
  echo
  echo "## Stack détectée"
  echo
  echo "- Thème(s) : $(tr '\n' ' ' < "$OUT/raw/themes.txt")"
  echo "- Constructeur : $BUILDER"
  echo "- Plugins visibles ($(wc -l < "$OUT/raw/plugins.txt")) :"
  sed 's/^/  - /' "$OUT/raw/plugins.txt"
  [ -s "$OUT/raw/generator.txt" ] && { echo; echo "- Generator :"; sed 's/^/  /' "$OUT/raw/generator.txt"; }
  echo
  echo "## SEO"
  echo '```'
  cat "$OUT/raw/seo.txt" 2>/dev/null
  echo '```'
  echo
  echo "## En-têtes HTTP"
  echo '```'
  tr -d '\r' < "$OUT/raw/home-headers.txt"
  echo '```'
  echo
  echo "## Ressources les plus lourdes"
  echo '```'
  sort -rn "$OUT/raw/assets-size.txt" 2>/dev/null | head -20 \
    | awk -F'\t' '{printf "%6d Ko  %s\n", $1/1024, $2}'
  echo '```'
  echo
  echo "---"
  echo
  [ -s "$OUT/PAGESPEED.md" ] && echo "Scores, Core Web Vitals, extensions et images : voir \`PAGESPEED.md\`."
  echo
  echo "Données brutes dans \`raw/\`. Pour l'analyse et le plan d'action : \`/site audit\`."
} > "$OUT/RAPPORT.md"

say "Terminé."
echo "  Rapport  : $OUT/RAPPORT.md"
echo "  Brut     : $OUT/raw/"
echo
echo "  Étape suivante dans Claude Code : /site audit"
