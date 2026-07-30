# Jarvis Starter Kit — Njaho

> Assistant personnel propulsé par Claude Code.

---

## Démarrage rapide

**Chaque session :** tapez `/prime` pour charger votre contexte complet.

**Chaque matin :** tapez `/morning` pour votre veille personnalisée.

**Après un changement important :** tapez `/update` pour mettre à jour vos fichiers.

---

## Serveurs MCP

| Serveur | Config | Authentification |
|---------|--------|------------------|
| `notion` | `@notionhq/notion-mcp-server` | `NOTION_TOKEN` dans `.env` |
| `plaud` | `@plaud-ai/mcp` (officiel) | OAuth navigateur au 1er lancement, aucune clé à stocker |

**Plaud :** au premier démarrage, le serveur ouvre votre navigateur pour vous connecter à votre compte Plaud et autoriser l'accès. Vos identifiants restent locaux, l'assistant ne voit jamais votre mot de passe. Une fois autorisé, Claude accède directement à vos enregistrements, transcriptions et résumés Plaud, sans passer par l'export Notion.

---

## Structure

```
jarvis/
├── CLAUDE.md                    # L'âme de votre assistant
├── context/
│   ├── CONTEXT.md               # Qui vous êtes, vos objectifs, vos projets
│   ├── HISTORY.md               # Journal de bord des sessions
│   └── import/                  # Déposez ici vos documents à analyser
├── .claude/
│   ├── commands/
│   │   ├── prime.md             # /prime : démarrer une session
│   │   ├── update.md            # /update : mettre à jour le contexte
│   │   └── morning.md           # /morning : veille matinale
│   └── skills/
│       └── recherche-actualites/ # Skill de veille personnalisée
└── module-installs/
    └── jarvis-install/          # Module d'installation initial
```

---

Créé avec le Jarvis Starter Kit de Yassine SDIRI, Communauté IA sur Skool.
