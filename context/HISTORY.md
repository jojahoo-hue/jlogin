# HISTORY.md

> Journal de bord évolutif. Mis à jour automatiquement par Claude après chaque session significative.
> Ne pas modifier manuellement. Utiliser `/update` pour déclencher une mise à jour.

---

## 2026-07-11

### Mise à jour de session — Audit et corrections du bot Telegram
- Connecteur Notion natif testé et validé : accès live en lecture aux pages (supervision NOC, art, spirituel). Bascule Option B pleinement opérationnelle.
- Bot Telegram audité. Corrections : modèle claude-sonnet-4-6 (inexistant) remplacé par claude-sonnet-5 dans telegram-bot.py et morning-briefing.py ; restriction sécurité au seul TELEGRAM_CHAT_ID (filters.Chat, CHAT_ID obligatoire) ; suppression du code mort speak() et pomodoro_auto().
- Nouvelle fonctionnalité : réponse vocale du bot (macOS say + ffmpeg → note vocale Opus), activable via VOICE_REPLY. Le bot répond en texte et en audio aux vocaux.
- Décision architecture : Notion NON branché sur le bot Telegram (Option 3). Le bot reste le canal rapide (contexte + Claude + vocal) ; le travail Notion se fait dans Claude Code via le connecteur OAuth. Séparation claire, un seul mécanisme Notion.
- Rappel : le bot Telegram est un Jarvis allégé (Claude + CLAUDE.md + CONTEXT.md), sans accès Notion/fichiers/skills.

### Mise à jour de session — Bascule Notion vers connecteur natif
- Décision : Notion passe du script Mac (Option A) au connecteur natif claude.ai en OAuth (Option B), accès live lecture/écriture depuis le cloud.
- Scripts sync-notion.py et plaud-auto-sync.sh dépréciés (conservés comme fallback hors-ligne, non supprimés).
- Ligne cron « Sync Plaud/Notion */2h » retirée de crontab-setup.sh.
- Commande /sync-notion mise à jour : connecteur natif prioritaire, script en fallback.
- CONTEXT.md mis à jour sur le canal Notion.
- Action Njaho : autoriser le connecteur Notion sur claude.ai (Réglages > Connecteurs) et sélectionner les pages à partager. Le connecteur n'est visible qu'après reconnexion de session.

### Mise à jour de session — Finalisation config MCP/projet
- MCP Notion (npx) retiré de .claude/settings.json : non fonctionnel en cloud (api.notion.com bloqué + NOTION_TOKEN absent). Option A confirmée : lecture Notion assurée par scripts/sync-notion.py depuis le Mac.
- Bug corrigé dans plaud-auto-sync.sh : push vers HEAD au lieu de la branche codée en dur claude/prime-tDwAc (les syncs partaient sur l'ancienne branche).
- Audit sécurité du dépôt : aucun secret en dur, tout passe par .env gitignoré.
- Point de sécurité toujours ouvert : régénérer le token Notion exposé le 6 juin.
- Recommandation notée : adopter une branche stable (main) comme point d'ancrage du Jarvis plutôt que les branches claude/prime-* changeantes.
- Commit poussé sur claude/prime-2hx48v.

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
