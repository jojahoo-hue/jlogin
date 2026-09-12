# Commande /corpus

> Gère la couche corpus : la matière première locale issue de Plaud et de Notion,
> sur laquelle s'appuie la rédaction des livres.

## Principe

Trois couches, et il faut les garder distinctes :

| Couche | Où | Contenu | Sert à |
|---|---|---|---|
| Froide | `corpus/fiches/*.md` (git) | transcriptions intégrales, résumés, en-tête YAML | le grep, la rédaction |
| Chaude | Notion `🎙️ Plaud Archive` | résumé, actions, thème, lien | la consultation mobile, le pilotage |
| Production | `livres/` + Notion `📖 Manuscrits` | chapitres rédigés | l'écriture |

Raison d'être de la couche froide : lire une transcription de 50 ko via le MCP Notion
coûte environ 15 000 tokens. Un grep sur le même contenu en local en coûte 500.
Sur dix sources, c'est un facteur 30. On ne rédige jamais depuis Notion.

## Sous-commandes

### /corpus export

Reconstruit la couche froide depuis Notion.

```bash
python3 scripts/corpus_export.py            # incrémental
python3 scripts/corpus_export.py --full     # tout réécrire
```

Nécessite un `.env` à la racine avec `NOTION_TOKEN`. Si le token manque, dis-le à
Njaho et arrête-toi, ne tente pas de contourner par le MCP : 1342 pages via MCP
représentent des millions de tokens pour un résultat qu'un script produit en quelques
minutes.

Après l'export, affiche le contenu de `corpus/INDEX.md`.

### /corpus listing

Produit l'inventaire Plaud complet. C'est la seule étape qui passe par le MCP,
parce que Claude seul a accès à Plaud.

1. Appelle `mcp__Plaud__list_files` page par page (`page_size: 100`), de la page 1
   jusqu'à obtenir une liste vide. Il y avait 1577 enregistrements au 2026-09-12.
2. Écris le résultat dans `corpus/plaud-listing.json` au format :

```json
{
  "genere_le": "2026-09-12T20:00:00",
  "total": 1577,
  "enregistrements": [
    {"id": "...", "name": "...", "created_at": "...", "duration": 11163000}
  ]
}
```

3. Lance `python3 scripts/plaud_gap.py` et présente le rapport.

### /corpus rattrapage [N]

Crée dans Notion les fiches manquantes listées par `corpus/plaud-manquants.json`.
Par lots de 20 par défaut, N sinon. Pour chaque enregistrement manquant :

1. `mcp__Plaud__get_note` pour le résumé (peu volumineux, c'est voulu)
2. `mcp__Notion__notion-create-pages` dans la base `🎙️ Plaud Archive`
   (`36f92f894f8c81b79bc5dbec08bf24d4`) avec Titre, Date, Durée, Plaud_ID,
   Résumé, Dossier, Thème
3. Statut `Résumé seul` si la transcription n'a pas été reprise, `Transcrit` sinon

N'appelle **jamais** `get_transcript` en boucle sur un long enregistrement pour
alimenter Notion : une séance de 3 h fait 190 000 caractères. Les transcriptions
se récupèrent par `corpus_export.py` une fois la fiche créée, ou pas du tout si
l'enregistrement n'a pas d'intérêt pour un livre.

Après chaque lot, annonce la progression et demande si on continue.

### /corpus themes

Applique la taxonomie contrôlée de `corpus/taxonomie.yaml` à Notion.

```bash
python3 scripts/notion_taxonomie.py            # rapport
python3 scripts/notion_taxonomie.py --apply    # écrit
```

Règle absolue : on n'ajoute jamais une valeur à `corpus/taxonomie.yaml` sans en
retirer une autre. C'est ce qui a fait exploser l'ancienne propriété Sujets à
5081 options, au point que la seule lecture du schéma coûtait 300 000 tokens.

## Recherche dans le corpus

```bash
# les fiches d'un thème
grep -l 'Sceaux et cartouches' corpus/fiches/*.md

# un terme dans les transcriptions, avec numéro de ligne
grep -rin 'kalunga' corpus/fiches/ | head -40

# les fiches destinées à un livre
grep -l 'livre_cible: "Nza Nga dia KiTuni"' corpus/fiches/*.md

# les sessions longues d'un thème donné
grep -l 'Retraites initiatiques' corpus/fiches/*.md | xargs grep -l 'duree_min: [0-9]\{3\}'
```

## Règles

- Ne jamais mettre de fichier audio dans Notion : plafond de 5 Mo par fichier sur
  le plan actuel, et aucun intérêt puisque l'audio reste sur Plaud
- Ne jamais rédiger depuis Notion, toujours depuis `corpus/fiches/`
- Toute opération destructive sur Notion exige que `corpus/index.json` existe,
  les scripts le vérifient et refusent de tourner sinon
- Signaler à Njaho si une fiche touche à des sujets privés avant de l'archiver
