# Jarvis Starter Kit — Njaho

> Assistant personnel propulsé par Claude Code.

---

## Démarrage rapide

**Chaque session :** tapez `/prime` pour charger votre contexte complet.

**Chaque matin :** tapez `/morning` pour votre veille personnalisée.

**Après un changement important :** tapez `/update` pour mettre à jour vos fichiers.

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

## Intégrations MCP

Serveurs MCP configurés dans `.claude/settings.json` :

- **notion** : accès à l'espace Notion (nécessite `NOTION_TOKEN` dans `.env`).
- **plaud** : accès aux enregistrements et transcriptions Plaud (`@plaud-ai/mcp`, authentification OAuth via navigateur). Activation en local : `npx -y @plaud-ai/mcp@latest install`.

---

Créé avec le Jarvis Starter Kit de Yassine SDIRI, Communauté IA sur Skool.
