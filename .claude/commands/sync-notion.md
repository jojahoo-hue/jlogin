# Commande /sync-notion

> Synchronise le contexte Jarvis depuis les pages Notion de Njaho.

## Modes

- **`/sync-notion`** (incrémental, défaut) : ne récupère que les éléments modifiés depuis `last_sync`. Rapide, utilisé aussi automatiquement par `/morning`.
- **`/sync-notion --full`** : balayage le plus large possible de toute la base, indépendamment de `last_sync`. Voir l'étape 2 bis.

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

### Étape 2 bis : Mode `--full` (balayage complet des archives ChatGPT)

À exécuter uniquement si l'argument `--full` est passé. Sert à rattraper les conversations qu'un sync incrémental aurait pu manquer.

Contrainte importante à connaître : le MCP Notion n'a **pas** d'endpoint de pagination de lignes, et `search` est plafonné à 25 résultats par appel sans curseur. Toutes les conversations partagent en plus la même date de création Notion (jour du déversement par l'extension), donc le filtrage par fenêtres de dates ne disperse rien. Conséquence : un `--full` via MCP est un **balayage best-effort, pas une garantie d'exhaustivité**.

Procédure :
1. Récupère le `data_source_id` de la source `chatgpt_archives` dans `notion-config.json`.
2. Lance plusieurs recherches `notion-search` scopées sur ce data source (`data_source_url: collection://<data_source_id>`, `page_size: 25`), avec des requêtes thématiques variées couvrant les grands domaines de Njaho. Au minimum : (a) tradition/paradigme Kôngo, (b) rituels/énergétique/médiumnité, (c) émotionnel/relationnel, (d) apprentissage/mémoire/calcul/QCM, (e) travail/télécom/programmation, (f) un terme générique comme « conversation ». Ajoute d'autres angles si tu soupçonnes des familles manquantes.
3. Fais l'union de tous les résultats et **dédoublonne par ID de page** (et compare aux entrées déjà présentes dans le fichier de destination).
4. Reconstruis ou complète `context/import/notion-chatgpt-archives.md` en classant les conversations par thème, avec un lien Notion par entrée. Signale les doublons réels repérés dans la base (même titre, IDs différents).
5. Mets `last_sync` à la date du jour.
6. Dans le rapport, précise clairement que l'exhaustivité n'est pas garantie et que `scripts/sync-notion.py` (pagination réelle via l'API) reste le filet de sécurité pour un export 100% complet.

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
