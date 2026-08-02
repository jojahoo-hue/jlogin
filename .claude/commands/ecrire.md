# Commande /ecrire

> Raccourci pour écrire un livre entier, de l'idée au manuscrit.
> Gère le projet dans la durée : concept, plan, rédaction chapitre par chapitre, suivi.
> À ne pas confondre avec `/livre` (digérer un livre) ni `/contenu livre` (un seul passage).

---

## Déclenchement

Quand Njaho tape `/ecrire [titre]` ou `/ecrire` seul.

Si aucun projet n'est précisé, d'abord vérifier s'il existe déjà des projets en cours
dans `context/import/livre-projets/`. Si oui, les lister :

```
Tu as ces projets de livre en cours :

1. [Titre] — [X/Y chapitres rédigés]
2. [Titre] — [X/Y chapitres rédigés]

Tu veux continuer l'un d'eux, ou démarrer un nouveau livre ?
```

Si aucun projet ou nouveau livre demandé, aller en Phase 1.

---

## Style de référence

Appliquer systématiquement le style initiatique de Njaho (voir `/contenu`) :
- **Initiatique et littéral** : chaque mot porte un sens, rien de décoratif
- **Ancré dans la tradition Congo** : forces cosmiques, énergies élémentaires, lignées ancestrales
- **Géo-mathématique** : la forme naît de la formule, la géométrie est sacrée
- **Universel** : accessible à plusieurs niveaux de lecture
- **Sobre et dense** : chaque phrase est une pierre posée, jamais d'ésotérisme vague

Ne jamais produire de texte générique sur « la spiritualité » sans ancrage dans le vécu de Njaho.

---

## Phase 1 : Cadrage du livre (le socle)

Poser ces questions, une fois, avant tout plan :

```
Nouveau livre. Quelques questions pour poser le socle :

1. Titre (ou titre provisoire) et sous-titre éventuel
2. Le sujet en une phrase — l'idée que le lecteur doit emporter
3. Pour qui ? (initié, curieux, grand public, lecteur de tes 2 premiers livres)
4. Pourquoi ce livre maintenant ? À quel objectif ou cheminement il répond
5. Format visé : essai, récit initiatique, manuel pratique, recueil
6. Longueur cible : nombre de chapitres estimé et pages/mots par chapitre
7. Ton : plutôt transmission directe, récit vécu, ou enseignement structuré
```

Synthétiser les réponses en une **fiche de projet** (voir Phase 6) avant d'aller plus loin.

---

## Phase 2 : Architecture du livre (le plan)

À partir de la fiche, proposer une **structure complète** :

```
ARCHITECTURE — [Titre]

Fil directeur : [la promesse tenue du début à la fin, en une phrase]

Partie I — [Titre de partie]
  Ch. 1 — [Titre] : [idée centrale en une ligne]
  Ch. 2 — [Titre] : [idée centrale]
Partie II — [Titre de partie]
  Ch. 3 — [Titre] : [idée centrale]
  ...

Progression : [comment le lecteur est transformé de la 1re à la dernière page]
```

Règles de structure :
- Chaque chapitre porte **une seule idée maîtresse**, pas plus
- L'ordre des chapitres suit une **progression initiatique** : le visible, le caché, le transmis
- Le premier chapitre pose une image concrète, le dernier ouvre plutôt qu'il ne referme

Faire valider le plan par Njaho avant de rédiger. Ajuster tant qu'il n'est pas juste.

---

## Phase 3 : Rédaction chapitre par chapitre

Ne jamais rédiger tout le livre d'un coup. Travailler **un chapitre à la fois**.

Avant chaque chapitre, confirmer :
```
On attaque le chapitre [N] — [Titre].
Idée maîtresse : [rappel].
Longueur cible : [X mots].

Tu as des notes, une expérience vécue, une formule ou un ancêtre à y ancrer ?
(Si oui, donne-les-moi. Sinon je pars du plan.)
```

Puis rédiger dans le style de Njaho :
- Ouvrir sur une affirmation ou une image concrète, jamais une question rhétorique
- Développer par strates : le visible, le caché, le transmis
- Ancrer chaque idée dans du concret : une forme, une couleur, une formule, une énergie, une lignée
- Conclure par une ouverture vers le chapitre suivant

Enregistrer chaque chapitre dans son fichier dédié (voir Phase 6).
Après rédaction, proposer une **relecture ciblée** : cohérence avec le fil directeur,
répétitions, densité. Ne pas passer au chapitre suivant tant que celui-ci n'est pas validé.

---

## Phase 4 : Suivi de progression

Maintenir à jour le **tableau de bord** du livre (dans la fiche de projet) :

```
PROGRESSION — [Titre]

[✓] Ch. 1 — [Titre]        1 850 mots   validé
[~] Ch. 2 — [Titre]        rédigé, en relecture
[ ] Ch. 3 — [Titre]        à écrire
...

Total rédigé : [X] mots / [Y] visés   ([Z] %)
Prochaine session : [chapitre à attaquer]
```

À chaque session, rappeler où on en est et proposer la prochaine étape.

---

## Phase 5 : Cohérence et finalisation

Quand tous les chapitres sont rédigés, proposer une **passe d'ensemble** :
- Vérifier que le fil directeur tient du premier au dernier chapitre
- Repérer les redites et les concepts introduits sans être définis
- Vérifier l'homogénéité du ton et du vocabulaire initiatique
- Proposer une introduction et une conclusion générale, écrites **en dernier**
- Suggérer un titre définitif et une 4e de couverture (accroche + promesse)

Assembler le manuscrit complet dans `context/import/livre-projets/[slug]/manuscrit.md`.

---

## Phase 6 : Fichiers et enregistrement

Chaque livre vit dans son dossier :

```
context/import/livre-projets/[slug]/
├── projet.md          # Fiche : cadrage, plan, tableau de progression
├── ch-01-[slug].md    # Un fichier par chapitre
├── ch-02-[slug].md
└── manuscrit.md       # Assemblage final (Phase 5)
```

**projet.md** contient :
```
# [Titre] — [Sous-titre]
Démarré le : [date]
Format : [essai / récit / manuel]   Public : [cible]
Lien avec : [objectif ou cheminement de Njaho]

## Idée maîtresse
[une phrase]

## Architecture
[le plan validé en Phase 2]

## Progression
[le tableau de bord de la Phase 4]

## Notes et matière première
[expériences, formules, citations, références à réutiliser]
```

À la création d'un projet et à chaque jalon (plan validé, livre terminé),
ajouter une entrée dans `context/HISTORY.md` :
```
## [date] — Livre en écriture
- Titre : [Titre]
- Étape : [projet lancé / plan validé / ch. N rédigé / manuscrit terminé]
- Lien : [objectif de Njaho]
```

---

## Règles

- **Un chapitre à la fois.** Ne jamais générer tout le livre en une seule fois : la densité s'y perd
- Toujours relier le livre à un cheminement ou objectif concret de Njaho
- Demander la matière première (vécu, formule, ancêtre, énergie) avant de rédiger un chapitre
- Respecter la longueur cible fixée en Phase 1 (min. 2000 mots/chapitre si demandé)
- Faire valider le plan avant de rédiger, et chaque chapitre avant de passer au suivant
- Introduction et conclusion générale s'écrivent **en dernier**, jamais en premier
- Si un chapitre touche aux civilisations africaines ou à la tradition Congo : enrichir avec le vocabulaire initiatique propre à Njaho
