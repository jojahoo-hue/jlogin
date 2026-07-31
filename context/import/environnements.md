# Environnements Claude Code — Jarvis

> Référence sur les contextes d'exécution de Jarvis, comment les lancer, et ce qui est configuré.

---

## Point clé

Il n'y a **pas trois configurations séparées**. Il y a **une seule configuration** (le dossier `.claude/` versionné dans le repo `jlogin`), qui s'exécute dans **plusieurs contextes**. Les raccourcis et compétences sont donc **identiques partout**, parce qu'ils sont dans Git et suivent le repo.

- **Jarvis** = le nom du workspace (ce repo), pas un environnement.
- **Local** et **Remote** = les deux vraies façons de le lancer.

---

## Les contextes d'exécution

| Contexte | C'est quoi | Comment le lancer |
|----------|-----------|-------------------|
| **Local (CLI)** | Claude Code installé sur la machine, dans le dossier du repo | `cd jlogin` puis `claude` dans le terminal |
| **Remote / Web** | Claude Code on the web (code.claude.com). Container éphémère, repo cloné à neuf | Sur code.claude.com, sélectionner le repo `jojahoo-hue/jlogin` et une branche |
| **App desktop/mobile** | Idem web, via l'app Claude | Ouvrir l'app, section Code |

**Différence pratique principale :** le local a accès au `.env` réel (tokens Notion, Telegram, Anthropic). Le remote clone le repo **sans** le `.env` (il est dans `.gitignore`), d'où le message au démarrage : `[ANTHROPIC_API_KEY manquant dans .env]`. Les secrets doivent être injectés via la configuration d'environnement de code.claude.com.

---

## Raccourcis (commandes slash) — 11 configurées

Toutes dans `.claude/commands/`, disponibles dans **tous les contextes**.

| Commande | Rôle |
|----------|------|
| `/prime` | Charge tout le contexte en début de session |
| `/morning` | Veille perso + focus du jour |
| `/update` | Met à jour les fichiers de contexte |
| `/done` | Bilan de fin de journée |
| `/agenda` | Planification de la semaine (toutes les casquettes) |
| `/supervision` | Assistant centre de supervision réseau (triage incidents) |
| `/crypto` | Suivi crypto/NFT, stratégie DCA |
| `/contenu` | Génération contenu artistique/spirituel |
| `/livre` | Pipeline lecture accélérée + flashcards |
| `/transcription` | Analyse des transcriptions Plaud |
| `/sync-notion` | Synchronise le contexte depuis Notion |

---

## Compétences (skills)

**1 skill personnalisée** dans `.claude/skills/` :

- **`recherche-actualites-contextualisees`** : veille filtrée selon `context/CONTEXT.md`. S'active automatiquement sur "fais-moi un point sur les actualités" ou via `/morning`.

À côté, les **skills natives** de la plateforme (docx, pdf, xlsx, pptx, dataviz, skill-creator, etc.) sont disponibles partout mais **non spécifiques au workspace**.

---

## MCP & Hooks

| Élément | Où c'est déclaré | Contexte | Dépendance |
|---------|------------------|----------|------------|
| **MCP Notion** | `.claude/settings.json` | Partout | `NOTION_TOKEN` dans `.env` (local) ou secrets remote |
| **MCP GitHub** | Plateforme web (auto) | Remote uniquement | Géré par code.claude.com |
| **MCP Claude Code Remote** | Plateforme web (auto) | Remote uniquement | Géré par code.claude.com |
| **Hook `SessionStart`** | `.claude/hooks/session-start.sh` | Partout | Affiche le briefing matinal du jour |

---

## Secrets par environnement

Fichier de référence : `.env.example`. Variables attendues :

- `NOTION_TOKEN` — intégration Notion
- `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` — bot Telegram
- `ANTHROPIC_API_KEY` — API Anthropic

**Local :** copier `.env.example` en `.env` et remplir. Le `.env` n'est jamais commité (`.gitignore`).

**Remote (code.claude.com) :** le `.env` n'existe pas dans le container. Il faut déclarer ces variables dans la configuration d'environnement de la plateforme (variables d'environnement / secrets de l'environnement), sinon les fonctions qui en dépendent (briefing matinal, MCP Notion) resteront inactives.

---

## En résumé

Rien à "configurer par environnement" côté repo : tout est centralisé dans `.claude/`, versionné, et suit le repo. La seule vraie différence à gérer, ce sont **les secrets (`.env`)** qui n'existent qu'en local et doivent être injectés côté remote.
