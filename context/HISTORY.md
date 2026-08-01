# HISTORY.md

> Journal de bord évolutif. Mis à jour automatiquement par Claude après chaque session significative.
> Ne pas modifier manuellement. Utiliser `/update` pour déclencher une mise à jour.

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
