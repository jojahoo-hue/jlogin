# Commande /ecrire-livre

> Pipeline complet d'écriture d'un livre à partir de notes brutes : collecte des sources,
> cadrage éditorial, architecture, rédaction chapitre par chapitre, relecture, export.
>
> Ne pas confondre avec `/livre`, qui sert à **digérer** un livre lu (lecture accélérée,
> flashcards, concepts Garden). `/ecrire-livre` sert à **produire** un livre.

---

## Déclenchement

Quand Njaho tape `/ecrire-livre [titre ou projet]`, ou quand il demande d'écrire un livre
à partir de notes, de conversations, de transcriptions ou d'un projet Notion.

Si aucun projet n'est fourni, demander :
```
Quel livre veux-tu écrire ?
Donne-moi le titre de travail et où se trouvent les notes sources.
```

---

## Phase 0 : Collecte des sources (bloquante)

**Aucune ligne du livre ne s'écrit tant que la matière n'est pas dans le dépôt.**
Un livre issu de notes ne s'invente pas : si la source manque, le texte produit serait
de la fiction plausible, pas la transmission de Njaho.

Vérifier dans cet ordre :

1. `livres/[projet]/notes-sources/` contient-il des fichiers ?
2. `context/import/` contient-il un export lié au projet ?
3. Sinon, Notion est-il accessible ? (MCP Notion actif, ou `NOTION_TOKEN` présent dans `.env`)

**Si Notion est inaccessible (cas du cloud Claude Code, `api.notion.com` bloqué) :**
proposer les trois voies, dans cet ordre de préférence :

```
Option A (recommandée) : sync depuis le Mac
  1. Ajouter la source dans notion-config.json (ID de la page projet)
  2. python3 scripts/sync-notion.py
  3. git add . && git commit && git push

Option B : export manuel
  Notion → ... → Exporter → Markdown & CSV → dézipper dans livres/[projet]/notes-sources/

Option C : copier-coller
  Coller les notes directement dans la conversation, je les classe dans notes-sources/
```

Ne jamais passer à la Phase 1 avec des sources partielles sans le dire explicitement.

---

## Phase 1 : Cadrage éditorial

Une fois les sources disponibles, les lire intégralement, puis poser ces questions :

```
Livre : [Titre de travail]
Sources lues : [nombre de fichiers, volume approximatif]

Cadrage :

1. À qui s'adresse ce livre ?
   a) Initiés / pratiquants déjà engagés dans la voie
   b) Grand public curieux, aucune connaissance préalable
   c) Chercheurs, milieu académique
   d) Transmission familiale / enfants

2. Quelle est la promesse du livre en une phrase ?
   (Ce que le lecteur sait ou vit après, qu'il ne savait pas avant)

3. Quel régime d'écriture ?
   a) Récit initiatique à la première personne (témoignage vécu)
   b) Enseignement structuré (exposé, transmission de la doctrine)
   c) Manuel de pratique (le lecteur fait, jour après jour)
   d) Mixte : récit + enseignement + pratique

4. Quel format de sortie ?
   Longueur visée, ePub / PDF / Word, auto-édition ou éditeur

5. Qu'est-ce qui ne doit PAS être écrit ?
   (Contenu réservé, non divulgable, secret initiatique, noms à protéger)
```

La question 5 est obligatoire pour tout contenu initiatique. Consigner la réponse dans
`livres/[projet]/PLAN.md` et la respecter sans exception dans toute la rédaction.

**Si Njaho délègue la question 5**, appliquer le périmètre par défaut, volontairement
restrictif, et le lui signaler comme desserrable :

- **Règle du seuil** : le livre dit ce qui se joue et ce que cela transforme, jamais
  comment l'exécuter seul. En cas de doute, l'élément sort du livre
- Ne s'écrivent pas : ce qui fut transmis sous secret explicite, le détail opératoire du
  rite (formules mot pour mot, gestes, matières, dosages, horaires), les noms de
  personnes sans accord écrit, les lieux précis, le vécu d'autrui, les noms sacrés dont
  l'énonciation est réglée, toute pratique corporelle reproductible sans encadrement
- S'écrivent sans réserve : le récit intérieur, le sens et la cosmologie, les effets sur
  la vie d'après, et la littérature ethnographique publiée citée comme telle avec sa
  source, jamais présentée comme transmission personnelle
- Marquer les cas limites par `> [RÉSERVÉ : ...]` et les soumettre à Njaho un par un

Le modèle complet est dans `livres/mbawu-21-jours/PLAN.md`, section 2.

**Vérifier aussi la visibilité du dépôt** avant de proposer de versionner des notes. Si le
dépôt est public, exclure `livres/*/notes-sources/**` du Git et le dire clairement : un
commit public reste récupérable dans l'historique même après suppression.

---

## Phase 2 : Architecture

Produire `livres/[projet]/PLAN.md` contenant :

- Titre, sous-titre, promesse en une phrase
- Public visé et régime d'écriture
- Table des matières complète, chapitre par chapitre
- Pour chaque chapitre : titre, intention en une ligne, sources mobilisées (fichiers et
  passages précis), longueur cible
- Ce qui reste hors du livre (réponse à la question 5)
- Trous identifiés : ce que les notes ne couvrent pas et qu'il faudra dicter ou compléter

**Faire valider le plan par Njaho avant d'écrire le moindre chapitre.** Un plan validé
évite de réécrire quinze chapitres après coup.

---

## Phase 3 : Rédaction

Un fichier par chapitre : `livres/[projet]/chapitres/NN-slug.md`.

Écrire **un chapitre à la fois**, puis s'arrêter et le soumettre. Ne pas enchaîner
cinq chapitres sans retour : la voix se cale sur les deux ou trois premiers.

Règles de rédaction :

- Écrire à partir des notes, pas de la culture générale. Chaque affirmation sur la
  tradition doit être traçable à une source dans `notes-sources/`
- Quand une notion est absente des notes mais nécessaire à la compréhension, ne pas
  l'inventer : insérer un marqueur `> [À COMPLÉTER : question précise pour Njaho]`
- Conserver le vocabulaire initiatique de Njaho tel quel, sans le traduire ni le lisser.
  Expliquer les termes en note ou dans le glossaire, jamais en les remplaçant
- Voix par défaut : première personne, français, phrases courtes, pas de tirets longs
- Pas de remplissage. Un chapitre court et dense vaut mieux qu'un chapitre étiré
- Tenir `livres/[projet]/glossaire.md` à jour au fil de la rédaction

---

## Phase 4 : Relecture

Après rédaction complète, trois passes distinctes, dans cet ordre :

1. **Passe fidélité** : chaque affirmation est-elle soutenue par les notes ? Lister
   les écarts. C'est la passe la plus importante sur un contenu initiatique
2. **Passe cohérence** : redites entre chapitres, contradictions, progression du lecteur,
   termes employés avant d'être définis
3. **Passe langue** : rythme, longueur de phrases, répétitions, ponctuation

Produire un rapport dans `livres/[projet]/relecture.md` avant de corriger.

---

## Phase 5 : Export

Assembler les chapitres dans `livres/[projet]/manuscrit.md`, puis selon le besoin :

- Word : utiliser la skill `docx`
- PDF : utiliser la skill `pdf`
- ePub : `pandoc manuscrit.md -o livre.epub` avec les métadonnées du PLAN.md

---

## Phase 6 : Suivi

Ajouter une entrée dans `context/HISTORY.md` :

```
## [date] — Livre en écriture : [Titre]
- Phase atteinte : [cadrage / plan validé / N chapitres écrits / relecture / export]
- Sources : [origine des notes]
- Décisions éditoriales : [public, régime d'écriture, périmètre]
- Prochaine étape : [action précise]
```

Mettre à jour `livres/[projet]/README.md` (tableau d'avancement) à chaque session.

---

## Règles

- La Phase 0 est bloquante. Pas de sources, pas de livre
- Ne jamais produire de contenu initiatique inventé, même vraisemblable. Le marqueur
  `> [À COMPLÉTER]` est toujours préférable à une belle phrase fausse
- Respecter absolument le périmètre de non-divulgation défini en Phase 1
- Un chapitre à la fois, validation avant d'enchaîner
- Njaho est l'auteur. Claude structure, rédige des propositions et signale les trous.
  La voix, la doctrine et les arbitrages restent à Njaho
