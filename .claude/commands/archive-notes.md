# Commande /archive-notes

> Archive les notes Apple (texte + photos) dans la base Notion "Archives Notes Apple".

## Ce que tu dois faire

### Étape 1 : Vérifier le terrain

Avant toute chose, vérifie que la session tourne bien sur le Mac de Njaho, car le script
lit Notes.app en local via AppleScript. Si tu es sur une machine distante (Claude Code sur
le web par exemple), dis-le franchement et propose la commande à lancer dans son terminal.

Vérifie ensuite :
- `.env` contient `NOTION_TOKEN` et `NOTION_NOTES_DB_ID`
- Les dépendances sont là : `pip3 install requests python-dotenv`

Si `NOTION_NOTES_DB_ID` est absent, propose de créer la base :
```
python3 scripts/apple-notes-to-notion.py --create-db
```
(demande d'abord l'id de la page Notion qui doit héberger la base, et rappelle qu'elle
doit être partagée avec l'intégration Notion)

### Étape 2 : Lancer la synchronisation

Premier archivage, ou après un doute, commence par un test :
```
python3 scripts/apple-notes-to-notion.py --limit 3
```

Puis la passe complète :
```
python3 scripts/apple-notes-to-notion.py
```

Options utiles selon la demande de Njaho :
- `--dry-run` : ne rien écrire dans Notion, juste compter ce qui serait envoyé
- `--full` : repousser toutes les notes, même celles déjà archivées
- `--limit N` : se limiter à N notes

Le script est incrémental : il ne retouche que les notes nouvelles ou modifiées depuis
la dernière passe, d'après `.apple-notes-state.json`.

### Étape 3 : Rapport

Lis `context/import/apple-notes-archive.md` et présente :

```
Archivage Notes Apple terminé.

Notes traitées : [nombre] ([créations] créations, [maj] mises à jour)
Photos envoyées : [nombre]
Notes verrouillées ignorées : [nombre]

Points d'attention :
- [le cas échéant : fichiers trop lourds, pièces jointes en échec]
```

Si des notes verrouillées ont été ignorées, rappelle qu'il faut les déverrouiller dans
Notes.app pour qu'AppleScript puisse les lire, il n'y a pas d'autre moyen.

---

## Règles

- Ne jamais supprimer de note dans Notes.app, l'archivage est une copie, pas une migration
- En cas d'échec d'autorisation AppleScript (erreur -1743), guider vers Réglages Système >
  Confidentialité et sécurité > Automatisation > Notes
- Si plus de 50 notes sont à traiter, prévenir que la passe peut prendre plusieurs minutes
  à cause de l'upload des photos
- Après un archivage important, proposer d'ajouter une entrée dans `context/HISTORY.md`
