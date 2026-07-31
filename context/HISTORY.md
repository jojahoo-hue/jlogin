# HISTORY.md

> Journal de bord évolutif. Mis à jour automatiquement par Claude après chaque session significative.
> Ne pas modifier manuellement. Utiliser `/update` pour déclencher une mise à jour.

---

## 2026-07-31

### Alimentation du contexte — Inspections QHSE et résumés de la veille (via MCP Notion / Plaud)

- Clarification : pas de MCP Plaud autonome. Plaud exporte vers Notion (base `🎙️ Plaud Archive`), et c'est le MCP Notion qui alimente le contexte Jarvis.
- Le MCP Notion (connecteur claude.ai) fonctionne dans la session web, contrairement à l'accès direct `api.notion.com` bloqué côté cloud (voir note du 2026-06-06).
- ID réel de la base Plaud renseigné dans `notion-config.json` (était en placeholder) : `36f92f894f8c81b79bc5dbec08bf24d4`.
- Création de `context/import/plaud-inspections-veille.md` : synthèse des inspections QHSE / Visite d'Inspection Commune (2 comptes rendus extraits, 2 analyses indexées) et des résumés de la veille (2026-07-30).
- En attente de validation : périmètre exact des « quatre inspections », et report des points structurants (PPA, binôme obligatoire, sécurisation des accès) dans `CONTEXT.md`.

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
