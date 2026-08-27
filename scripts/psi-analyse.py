#!/usr/bin/env python3
"""
psi-analyse.py — Transforme un rapport PageSpeed Insights (JSON) en diagnostic
lisible pour un site WordPress.

Usage :
    python3 scripts/psi-analyse.py rapport.json [rapport-desktop.json]

Le JSON s'obtient avec :
    curl -sS "https://www.googleapis.com/pagespeedonline/v5/runPagespeed\
?url=https://njaho.com&strategy=mobile\
&category=performance&category=seo&category=accessibility&category=best-practices" \
      -o psi-mobile.json

Au-delà des scores, Lighthouse liste toutes les ressources chargées par la page.
On en déduit le thème actif, les extensions WordPress, les polices distantes et
les images non optimisées, sans jamais se connecter à l'administration du site.
"""

import json
import re
import sys
from collections import defaultdict

SEUILS = {  # (bon, à améliorer) en unités de la métrique
    "largest-contentful-paint": (2500, 4000),
    "cumulative-layout-shift": (0.1, 0.25),
    "total-blocking-time": (200, 600),
    "interactive": (3800, 7300),
}


def ko(octets):
    return f"{octets / 1024:.0f} Ko"


def charger(chemin):
    with open(chemin, encoding="utf-8") as f:
        data = json.load(f)
    if "error" in data:
        raise SystemExit(f"Erreur PageSpeed : {data['error'].get('message', '')}")
    return data


def bloc_scores(lh, strategie):
    print(f"\n## Scores ({strategie})\n")
    libelles = {
        "performance": "Performance",
        "accessibility": "Accessibilité",
        "best-practices": "Bonnes pratiques",
        "seo": "Référencement",
    }
    for cle, cat in lh.get("categories", {}).items():
        score = cat.get("score")
        if score is None:
            continue
        note = int(score * 100)
        etat = "bon" if note >= 90 else ("moyen" if note >= 50 else "faible")
        print(f"- {libelles.get(cle, cle):18s} {note:3d}/100  ({etat})")


def bloc_vitals(audits):
    print("\n## Core Web Vitals\n")
    noms = {
        "largest-contentful-paint": "LCP (affichage du contenu principal)",
        "cumulative-layout-shift": "CLS (stabilité visuelle)",
        "total-blocking-time": "TBT (réactivité)",
        "speed-index": "Speed Index",
        "first-contentful-paint": "FCP (premier affichage)",
        "interactive": "TTI (interactivité)",
    }
    for cle, libelle in noms.items():
        a = audits.get(cle, {})
        valeur = a.get("displayValue")
        if not valeur:
            continue
        brut = a.get("numericValue")
        verdict = ""
        if cle in SEUILS and brut is not None:
            bon, moyen = SEUILS[cle]
            verdict = " [bon]" if brut <= bon else (
                " [à améliorer]" if brut <= moyen else " [mauvais]")
        print(f"- {libelle:38s} {valeur}{verdict}")

    lcp = audits.get("largest-contentful-paint-element", {})
    items = lcp.get("details", {}).get("items", [])
    if items:
        sous = items[0].get("items", [{}])
        if sous:
            extrait = sous[0].get("node", {}).get("snippet", "")
            if extrait:
                print(f"\n  Élément le plus lent à s'afficher :\n    {extrait[:180]}")


def bloc_opportunites(audits):
    print("\n## Ce qui ralentit le site\n")
    lignes = []
    for a in audits.values():
        det = a.get("details", {})
        if det.get("type") != "opportunity":
            continue
        ms = det.get("overallSavingsMs", 0) or 0
        octets = det.get("overallSavingsBytes", 0) or 0
        if ms < 50 and octets < 20000:
            continue
        lignes.append((ms, octets, a.get("title", ""), a.get("description", "")))
    if not lignes:
        print("Aucune optimisation majeure détectée.")
        return
    for ms, octets, titre, _ in sorted(lignes, reverse=True)[:10]:
        gain = f"~{int(ms)} ms" if ms else ""
        if octets:
            gain += f" / {ko(octets)}" if gain else ko(octets)
        print(f"- {titre} ({gain})")


def bloc_diagnostics(audits):
    echecs = []
    for cle, a in audits.items():
        score = a.get("score")
        mode = a.get("scoreDisplayMode")
        if mode in ("notApplicable", "informative", "manual") or score is None:
            continue
        if score < 0.9:
            echecs.append((score, a.get("title", cle)))
    if not echecs:
        return
    print("\n## Points à corriger (audits en échec)\n")
    for score, titre in sorted(echecs)[:25]:
        print(f"- [{score:.1f}] {titre}")


def bloc_ressources(audits):
    """Analyse le détail réseau : poids par type, ressources les plus lourdes."""
    items = audits.get("network-requests", {}).get("details", {}).get("items", [])
    if not items:
        return None
    print("\n## Poids de la page\n")
    par_type = defaultdict(lambda: [0, 0])  # type -> [octets, nombre]
    total = 0
    for it in items:
        taille = it.get("transferSize", 0) or 0
        typ = it.get("resourceType", "Autre")
        par_type[typ][0] += taille
        par_type[typ][1] += 1
        total += taille
    print(f"Total transféré : {ko(total)} sur {len(items)} requêtes\n")
    for typ, (octets, nb) in sorted(par_type.items(), key=lambda x: -x[1][0]):
        print(f"- {typ:12s} {ko(octets):>10s}  ({nb} requêtes)")

    print("\n### Les 12 ressources les plus lourdes\n")
    for it in sorted(items, key=lambda x: -(x.get("transferSize", 0) or 0))[:12]:
        url = it.get("url", "")
        print(f"- {ko(it.get('transferSize', 0) or 0):>9s}  {url[:110]}")
    return items


def bloc_wordpress(items, hote_principal=""):
    """Déduit thème, extensions et polices distantes depuis les URL chargées."""
    if not items:
        return
    # Le domaine du site, pour distinguer ses ressources de celles des tiers.
    racine = ".".join(hote_principal.split(".")[-2:]) if hote_principal else ""
    urls = [it.get("url", "") for it in items]
    poids = {it.get("url", ""): it.get("transferSize", 0) or 0 for it in items}

    themes, plugins = set(), defaultdict(int)
    for u in urls:
        m = re.search(r"wp-content/themes/([^/?]+)", u)
        if m:
            themes.add(m.group(1))
        m = re.search(r"wp-content/plugins/([^/?]+)", u)
        if m:
            plugins[m.group(1)] += poids.get(u, 0)

    print("\n## Empreinte WordPress déduite des ressources chargées\n")
    print(f"- Thème : {', '.join(sorted(themes)) or 'non identifié'}")
    if plugins:
        print(f"- Extensions chargées sur la page d'accueil : {len(plugins)}")
        for nom, octets in sorted(plugins.items(), key=lambda x: -x[1]):
            print(f"    - {nom:38s} {ko(octets):>10s}")
        lourds = [n for n, o in plugins.items() if o > 100000]
        if lourds:
            print(f"\n  Extensions de plus de 100 Ko sur l'accueil : {', '.join(lourds)}")
            print("  Chacune doit justifier sa présence, sinon elle sort.")
    else:
        print("- Aucune extension détectée dans les ressources (bon signe, ou "
              "ressources fusionnées par le cache)")

    builders = {
        "elementor": "Elementor",
        "js_composer": "WPBakery",
        "fusion": "Avada Fusion",
        "divi|et_pb": "Divi",
        "bricks": "Bricks",
        "kadence": "Kadence",
        "blocksy": "Blocksy",
        "generatepress": "GeneratePress",
    }
    joint = " ".join(urls).lower()
    trouves = [nom for motif, nom in builders.items() if re.search(motif, joint)]
    if trouves:
        print(f"- Thème ou constructeur reconnu : {', '.join(trouves)}")

    distants = defaultdict(int)
    for u in urls:
        m = re.match(r"https?://([^/]+)", u)
        if m and (not racine or not m.group(1).endswith(racine)):
            distants[m.group(1)] += poids.get(u, 0)
    if distants:
        print("\n- Domaines tiers appelés par la page :")
        for hote, octets in sorted(distants.items(), key=lambda x: -x[1]):
            note = ""
            if "fonts.g" in hote:
                note = "  <- polices à héberger localement (perf + RGPD)"
            elif "google-analytics" in hote or "googletagmanager" in hote:
                note = "  <- nécessite une bannière de consentement"
            print(f"    - {hote:40s} {ko(octets):>10s}{note}")


def bloc_images(audits):
    print("\n## Images\n")
    trouve = False
    for cle, libelle in (
        ("uses-optimized-images", "Images mal compressées"),
        ("modern-image-formats", "Images pas au format WebP/AVIF"),
        ("uses-responsive-images", "Images trop grandes pour leur affichage"),
        ("offscreen-images", "Images hors écran chargées quand même"),
        ("unsized-images", "Images sans dimensions déclarées (provoque du CLS)"),
    ):
        a = audits.get(cle, {})
        items = a.get("details", {}).get("items", [])
        if not items:
            continue
        trouve = True
        gain = a.get("details", {}).get("overallSavingsBytes", 0) or 0
        print(f"\n**{libelle}** — {len(items)} image(s)"
              + (f", {ko(gain)} récupérables" if gain else ""))
        for it in items[:6]:
            url = it.get("url", "")
            eco = it.get("wastedBytes", 0) or 0
            print(f"  - {url.split('/')[-1][:70]}"
                  + (f"  ({ko(eco)} de trop)" if eco else ""))
    if not trouve:
        print("Rien à signaler sur les images.")


def bloc_accessibilite(lh):
    audits = lh.get("audits", {})
    refs = (lh.get("categories", {}).get("accessibility", {}).get("auditRefs", []))
    echecs = [audits.get(r["id"], {}) for r in refs
              if audits.get(r["id"], {}).get("score") == 0]
    if not echecs:
        return
    print("\n## Accessibilité (compte aussi pour le référencement)\n")
    for a in echecs[:12]:
        nb = len(a.get("details", {}).get("items", []))
        print(f"- {a.get('title', '')}" + (f" ({nb} élément(s))" if nb else ""))


def bloc_seo(lh):
    audits = lh.get("audits", {})
    refs = lh.get("categories", {}).get("seo", {}).get("auditRefs", [])
    echecs = [audits.get(r["id"], {}) for r in refs
              if audits.get(r["id"], {}).get("score") == 0]
    print("\n## Référencement\n")
    if not echecs:
        print("Aucun blocage technique détecté par Lighthouse.")
    else:
        for a in echecs:
            print(f"- {a.get('title', '')}")


def bloc_crux(data):
    crux = data.get("loadingExperience", {}).get("metrics")
    if not crux:
        print("\n## Données de terrain\n\nPas assez de trafic réel mesuré par "
              "Google pour ce site (normal sur un site peu visité).")
        return
    print("\n## Données de terrain (visiteurs réels, 28 derniers jours)\n")
    noms = {
        "LARGEST_CONTENTFUL_PAINT_MS": "LCP",
        "CUMULATIVE_LAYOUT_SHIFT_SCORE": "CLS",
        "INTERACTION_TO_NEXT_PAINT": "INP",
        "FIRST_CONTENTFUL_PAINT_MS": "FCP",
        "EXPERIMENTAL_TIME_TO_FIRST_BYTE": "TTFB",
    }
    for cle, m in crux.items():
        print(f"- {noms.get(cle, cle):6s} {m.get('percentile')} "
              f"({m.get('category')})")


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)

    for i, chemin in enumerate(sys.argv[1:]):
        data = charger(chemin)
        lh = data.get("lighthouseResult", {})
        audits = lh.get("audits", {})
        strategie = data.get("lighthouseResult", {}).get(
            "configSettings", {}).get("formFactor", "?")

        if i == 0:
            print(f"# Audit PageSpeed — {data.get('id', '')}")
            print(f"\nAnalysé le {lh.get('fetchTime', '')[:19].replace('T', ' ')} UTC")
            print(f"URL finale : {lh.get('finalUrl', data.get('id', ''))}")

        bloc_scores(lh, strategie)

        if i == 0:  # détail complet sur le mobile uniquement
            bloc_vitals(audits)
            bloc_crux(data)
            bloc_opportunites(audits)
            items = bloc_ressources(audits)
            url_finale = lh.get("finalUrl", data.get("id", ""))
            hote = re.sub(r"^https?://([^/]+).*", r"\1", url_finale)
            bloc_wordpress(items, hote)
            bloc_images(audits)
            bloc_seo(lh)
            bloc_accessibilite(lh)
            bloc_diagnostics(audits)

    print("\n---\n\nCe rapport ne voit que ce qui est public. Il ne dit rien des "
          "versions de WordPress et PHP, des extensions désactivées, des comptes "
          "utilisateurs ni des sauvegardes. Ces points restent à vérifier dans "
          "l'administration du site.")


if __name__ == "__main__":
    main()
