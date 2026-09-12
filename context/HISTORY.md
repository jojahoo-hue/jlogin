# HISTORY.md

> Journal de bord évolutif. Mis à jour automatiquement par Claude après chaque session significative.
> Ne pas modifier manuellement. Utiliser `/update` pour déclencher une mise à jour.

---

## 2026-09-12

### Inventaire Plaud et mise en place de la chaîne corpus vers manuscrit

**Inventaire réalisé**
- 1 577 enregistrements sur le compte Plaud, d'octobre 2024 à septembre 2026
- 1 342 déjà exportés dans la base Notion `🎙️ Plaud Archive`, soit 1 205 heures d'audio
- 235 enregistrements manquants dans Notion, à rattraper
- Chaque fiche Notion contient déjà résumé, actions, sujets et transcription intégrale
- Certaines fiches Plaud n'ont ni transcription ni résumé, repérables à leur nom
  (horodatage brut au lieu d'un titre), y compris un enregistrement de 74 minutes

**Problèmes identifiés**
- La propriété `Sujets` de Plaud Archive comptait 5 081 options de multi-select.
  La seule lecture du schéma coûtait environ 300 000 tokens par session.
- Erreurs de classement constatées : cours initiatiques rangés en Télécom
- Base Manuscrits : 107 lignes pour 86 titres distincts et 39 numéros distincts
  sur Thot Mfumu TuTi dia Tiya, donc doublons et collisions de numérotation

**Décisions prises**
- Architecture à trois couches : corpus local en markdown pour la rédaction,
  Notion pour le pilotage et la consultation, `livres/` pour la production
- On ne rédige jamais depuis Notion. Lire une transcription de 50 ko via MCP coûte
  environ 15 000 tokens, un grep local environ 500.
- Taxonomie contrôlée à 40 thèmes figée dans `corpus/taxonomie.yaml`, avec la règle
  de ne jamais ajouter une valeur sans en retirer une autre
- Le transfert de masse passe par des scripts qui tapent l'API Notion directement,
  pas par le MCP, dont le quota de lecture a été atteint dès la quatrième requête
- Les transcriptions ne sont pas versionnées par défaut, décision de diffusion
  laissée à Njaho (trois options documentées dans `corpus/README.md`)

**Livré**
- `corpus/taxonomie.yaml`, 40 thèmes, 314 alias, mappés vers les 9 livres
- `scripts/corpus_lib.py`, client Notion sans dépendance externe
- `scripts/corpus_export.py`, Notion vers corpus local, incrémental
- `scripts/notion_taxonomie.py`, refonte de la taxonomie, avec garde-fous
- `scripts/manuscrits_dedup.py`, sauvegarde puis dédoublonnage et renumérotation
- `scripts/plaud_gap.py`, écart entre Plaud et Notion
- `scripts/corpus_setup.sh`, enchaînement dans l'ordre sûr
- Commandes `/corpus` et `/manuscrit`

**En attente**
- Exécution des scripts sur le Mac, un `.env` avec `NOTION_TOKEN` est requis
- Rattrapage des 235 enregistrements manquants
- Choix du mode de versionnement du corpus

---

## 2026-06-06

### Mise à jour de session — Configuration Jarvis et intégration Notion

- Jarvis Starter Kit déployé sur le dépôt `jojahoo-hue/jlogin`, branche `claude/prime-tDwAc`
- Intégration Notion configurée : MCP Notion dans `.claude/settings.json`, commande `/sync-notion`, script Python `scripts/sync-notion.py`
- Contrainte identifiée : le cloud Claude Code bloque `api.notion.com`, la sync Notion doit tourner depuis le Mac local
- Décision retenue : sync Notion via script Python sur Mac puis push git (Option A)
- Action de sécurité en attente : régénérer le token Notion exposé accidentellement dans le chat
- Claude Code (Jarvis) adopté comme assistant principal en remplacement de ChatGPT

---

## 2026-06-06

### Installation initiale du Jarvis

- Workspace personnalisé pour Njaho, basé à Fort-de-France, Martinique
- Profil principal : Mix — Ingénieur / Entrepreneur / Chercheur / Artiste / Père
- Activité : Responsable d'exploitation et formations dans un opérateur télécom, 20 ans d'expertise
- Objectifs court terme identifiés : automatisation du centre de supervision, lancement site artistique, migration ChatGPT vers Claude
- Vision long terme : département de résilience réseau, oeuvre artistique/spirituelle reconnue, livres publiés, association culturelle développée
- Projets actifs au démarrage : digitalisation centre de supervision, série géo-mathématique, série Congo/Soleil, formation énergies élémentaires, écriture de livres, migration ChatGPT vers Claude
- Domaine d'aide prioritaire : apprentissage et formation, lecture efficace, neurosciences appliquées
- Style de communication choisi : mélange selon contexte (direct pour opérationnel, détaillé pour conceptuel)
- Jarvis Starter Kit installé depuis les fichiers uploadés, profil déjà configuré
