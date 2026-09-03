# HISTORY.md

> Journal de bord évolutif. Mis à jour automatiquement par Claude après chaque session significative.
> Ne pas modifier manuellement. Utiliser `/update` pour déclencher une mise à jour.

---

## 2026-08-27

### Ouverture du chantier livre — Mbawu, les vingt-et-un jours

- Nouveau projet de livre lancé à partir du projet Notion Nza Ngai dia Nzayi
- Constat : la commande `/livre` existante sert à digérer une lecture, pas à écrire. Création de la commande `/ecrire-livre`, pipeline d'écriture en 6 phases avec Phase 0 de collecte des sources bloquante
- Chantier créé dans `livres/mbawu-21-jours/` : README de pilotage, PLAN.md de cadrage, glossaire, dossier notes-sources
- Architecture proposée à valider : 21 chapitres, un par jour, regroupés en 3 cycles de 7. Hypothèse structurelle, à confirmer ou à jeter après lecture des notes
- Blocage confirmé : Notion inaccessible depuis le cloud Claude Code (`api.notion.com` filtré, aucun `NOTION_TOKEN`). Aucun chapitre ne sera écrit avant import des notes
- Source `Nza Ngai dia Nzayi` ajoutée dans `notion-config.json`, ID à renseigner pour la sync depuis le Mac
- Prochaine étape : importer les notes dans `livres/mbawu-21-jours/notes-sources/`, puis trancher les 5 questions de cadrage éditorial

### Mise à jour de contexte

- `CONTEXT.md` enrichi sur validation de Njaho : ajout du projet de livre "Mbawu, les vingt-et-un jours" dans les projets en cours
- Ajout d'une note durable sur l'accès Notion depuis Claude Code : connecteur installé et activé mais non authentifié, flux OAuth impossible en session non interactive, et `api.notion.com` filtré par le proxy réseau. Seules voies fiables : sync depuis le Mac ou export Markdown manuel

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
