# Commande /manuscrit

> Rédige un livre à partir du corpus Plaud, chapitre par chapitre, en citant ses sources.
>
> À ne pas confondre avec `/livre`, qui sert à **digérer** un livre lu. `/manuscrit`
> sert à **écrire** les siens.

## Les livres en cours

| Livre | Thèmes sources | Chapitres au 2026-09-12 |
|---|---|---|
| Thot Mfumu TuTi dia Tiya | Géométrie sacrée, Numérologie | 107 lignes, 86 titres distincts |
| Nza Nga dia KiTuni | Kalunga et mort, Lignées, Ancêtres | 58 |
| Nza Ngai dia Ndosi | Retraites RIK/RSK, Rêve et décorporation | 57 |
| Nza Ngai dia Nzayi | Cosmologie Kongo, Muntu, Éthique communautaire | 32 |
| Tablette de Thot | Kemet, Égypte et Nubie | 18 |
| Nza Nga dia Mbazi | Protection énergétique, Longo, Couple | 11 |
| Nza ngai Sono Zi Tiya | Sceaux et cartouches, Sono-zi-tiya | à démarrer |
| Leadership Totémique | Totems, Leadership, Abondance | à démarrer |
| Mpévé Ya Bakala | Méditation guidée | à démarrer |

La correspondance thème vers livre est portée par `corpus/taxonomie.yaml`,
champ `livre` de chaque thème. C'est la source de vérité.

## Prérequis

`corpus/index.json` doit exister. Sinon, lance `/corpus export` d'abord et arrête-toi.

## /manuscrit <livre> plan

Construit ou révise la table des chapitres.

1. Lis `corpus/INDEX.md` pour connaître le volume disponible sur les thèmes du livre
2. Liste les fiches sources : `grep -l 'livre_cible: "<livre>"' corpus/fiches/*.md`
3. Lis uniquement les **en-têtes YAML et les résumés** de ces fiches, jamais les
   transcriptions à ce stade. Un `sed -n '1,40p'` par fiche suffit.
4. Lis les chapitres déjà écrits dans `livres/<slug>/chapitres/`
5. Propose une table des chapitres au format :

```
PLAN — <Livre>

Partie I — <titre de partie>
  1. <titre du chapitre>
     Sources : 3 fiches (12 h) — corpus/fiches/2026-07-17_*.md, ...
     Angle : <en une phrase>
     Statut : à écrire

  2. ...
```

6. Signale les chapitres déjà rédigés qui ne trouvent pas leur place dans le plan,
   et les trous : les thèmes riches en heures mais sans chapitre.
7. Écris le plan dans `livres/<slug>/PLAN.md` après confirmation de Njaho.

## /manuscrit <livre> chapitre <N>

Rédige un chapitre.

1. Lis `livres/<slug>/PLAN.md` pour récupérer l'angle et les sources du chapitre N
2. Lis **intégralement** les fiches sources désignées, transcription comprise.
   C'est le seul moment où on lit les transcriptions en entier.
3. Rédige le chapitre en respectant ces contraintes :
   - français, voix de Njaho, ton de transmission et non de cours magistral
   - pas de tirets longs, ni em dash ni en dash, virgules ou points
   - le vocabulaire kikongo est conservé tel quel, expliqué à sa première occurrence,
     jamais traduit à la va-vite
   - les citations de Mfumu Nswadi Kimbazi sont marquées comme telles et fidèles
   - chaque affirmation qui vient d'une session porte une note de source
4. Écris `livres/<slug>/chapitres/NN-<titre-slug>.md` avec un en-tête YAML :

```yaml
---
livre: "<Livre>"
numero: N
titre: "<Titre>"
statut: Brouillon
methode: <SOSRAC | Vibratoire | Numérologie | Sono-zi-tiya | Journaling | Mémoire Vivante | Castaneda | Transmission Vivante>
mots: <compte réel>
sources:
  - corpus/fiches/....md
date: AAAA-MM-JJ
---
```

5. Propose ensuite de créer la ligne Notion dans `📖 Manuscrits`
   (`36f92f894f8c810ab451f42c4b319cd7`). Attends la confirmation.

**Ne crée jamais un chapitre dont le numéro existe déjà pour ce livre.** Vérifie
d'abord avec `grep -h 'numero:' livres/<slug>/chapitres/*.md | sort -n`. La base
Manuscrits a déjà souffert de collisions de numéros, c'est ce que corrige
`scripts/manuscrits_dedup.py`.

## /manuscrit <livre> revue

Contrôle de cohérence sur un livre entier.

1. Doublons de titre et collisions de numéro : `python3 scripts/manuscrits_dedup.py --livre "<Livre>"`
2. Vérifie que chaque chapitre cite au moins une source du corpus
3. Repère les répétitions d'un chapitre à l'autre, les notions définies deux fois
4. Construit ou met à jour le glossaire kikongo dans `livres/<slug>/GLOSSAIRE.md`,
   une entrée par terme, avec le chapitre de première occurrence
5. Produit un rapport dans `reports/revue-<slug>.md`

## /manuscrit <livre> export

Assemble le manuscrit complet.

1. Concatène les chapitres dans l'ordre des numéros
2. Écrit `livres/<slug>/<slug>-complet.md` avec une table des matières
3. Si Njaho veut un `.docx` ou un `.pdf`, utilise la skill `anthropic-skills:docx`
   ou `anthropic-skills:pdf`
4. Annonce le nombre de mots, de chapitres et de sources citées

## Règles

- Une session de rédaction traite **un seul chapitre**. Un chapitre représente
  déjà la lecture de plusieurs transcriptions longues.
- Ne jamais inventer un enseignement. Si le corpus ne dit rien sur un point du
  plan, le signaler et proposer d'enregistrer une session Plaud dédiée.
- Distinguer systématiquement ce qui vient de l'enseignement reçu et ce qui vient
  de la réflexion propre de Njaho. Le lecteur doit pouvoir faire la différence.
- Toujours relier au projet d'ensemble : élévation de conscience et transmission
  du cheminement initiatique.
- Après chaque chapitre rédigé, ajouter une entrée dans `context/HISTORY.md`.
