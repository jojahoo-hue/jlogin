# Commande /sync-notion

> Synchronise le contexte Jarvis depuis les pages Notion de Njaho.

## Ce que tu dois faire

### Étape 1 : Lire la configuration

Lis le fichier `notion-config.json` à la racine du projet pour connaître :
- Les IDs des pages/bases de données à synchroniser
- Le type de chaque page (archives ChatGPT, résumés, transcriptions, projets)
- Le fichier de destination pour chaque source

### Étape 2 : Récupérer les pages Notion

Pour chaque source dans la config, utilise les outils MCP Notion pour :
1. Récupérer le contenu de la page ou de la base de données
2. Extraire le texte pertinent (titre, contenu, propriétés clés)
3. Filtrer les éléments mis à jour depuis la dernière synchronisation

### Étape 3 : Mettre à jour les fichiers de contexte

Selon le type de contenu récupéré :

**Archives ChatGPT (conversations)**
- Extraire les décisions importantes, projets mentionnés, informations clés
- Mettre à jour `context/CONTEXT.md` si de nouveaux projets ou objectifs sont détectés
- Ajouter les éléments nouveaux dans `context/import/notion-chatgpt-archives.md`

**Résumés de sessions**
- Lire le contenu des résumés
- Si un résumé contient un changement de projet ou d'objectif, proposer une mise à jour de CONTEXT.md
- Archiver dans `context/import/notion-resumes.md`

**Transcriptions**
- Extraire les passages clés (décisions, insights, apprentissages)
- Archiver dans `context/import/notion-transcriptions.md`

**Pages de projets**
- Comparer avec les projets listés dans CONTEXT.md
- Signaler les nouveaux projets ou les projets terminés
- Proposer une mise à jour si nécessaire

### Étape 4 : Rapport de synchronisation

Présente un résumé de la sync :

```
Synchronisation Notion terminée.

Pages lues : [nombre]
Dernière mise à jour Notion : [date]

Nouveautés détectées :
- [Élément 1 : description]
- [Élément 2 : description]

Fichiers mis à jour :
- [fichier 1]
- [fichier 2]

Mises à jour de contexte proposées :
[Si des changements importants détectés, lister les propositions]
```

---

## Règles

- Ne jamais écraser du contenu existant sans confirmation
- Si un conflit existe entre le contexte Jarvis et Notion, signaler les deux versions et demander laquelle est à jour
- Toujours ajouter une entrée dans HISTORY.md après une sync réussie
- Si l'API Notion n'est pas accessible (token manquant, page non connectée), utiliser le script Python de fallback : `python3 scripts/sync-notion.py`
