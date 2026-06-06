# Commande /livre

> Pipeline complet de digestion d'un livre : lecture accélérée, notes, concepts, flashcards.
> Inspiré de la méthode Stéphane D. (x20 vitesse de lecture via Readwise + audio).

---

## Déclenchement

Quand Njaho tape `/livre [titre]` ou `/livre` seul.

Si aucun titre fourni, demander :
```
Quel livre veux-tu digérer ?
Donne-moi le titre et l'auteur.
```

---

## Phase 1 : Cadrage (2 minutes)

Poser ces questions :

```
Livre : [Titre] — [Auteur]

Quelques questions rapides :

1. Tu as le livre sous quelle forme ?
   a) ePub / PDF
   b) Papier uniquement
   c) Audio uniquement
   d) ePub + Audio (idéal pour la méthode Readwise x3)

2. Pourquoi ce livre maintenant ? À quel projet ou objectif il répond ?
   (Cela oriente les concepts à extraire)

3. Combien de temps tu peux y consacrer cette semaine ?
   (Ex : "3 sessions de 25 min", "1h ce week-end")
```

---

## Phase 2 : Plan de lecture accélérée

Selon le format disponible, recommander la méthode adaptée :

**Si ePub + Audio disponibles (méthode optimale) :**
```
Méthode Readwise Reader — vitesse x20

1. Importer l'ePub dans Readwise Reader
2. Activer la lecture audio simultanée
3. Démarrer à x1.5, monter à x2 puis x3 progressivement
4. Sessions de 25 minutes (Pomodoro)
5. Surligner les passages clés directement dans Readwise

Estimation : [calcul basé sur nb de pages estimé] sessions de 25 min
```

**Si PDF ou papier uniquement :**
```
Méthode lecture active

1. Lire la table des matières et l'introduction (vue d'ensemble)
2. Lire les conclusions de chaque chapitre d'abord
3. Lire le corps en mode "chasse aux idées clés"
4. Annoter directement ou dans Notion
```

**Si Audio uniquement :**
```
Méthode écoute active

1. Écouter à x1.5 en premier passage
2. Réécouter les passages clés à x1
3. Dicter les idées clés dans Plaud après chaque session
4. Exporter la transcription Plaud → context/import/ → /transcription
```

---

## Phase 3 : Extraction des idées clés

Après que Njaho a lu / écouté le livre, demander :

```
Tu as terminé le livre (ou une partie). Donne-moi :

1. Les 3 à 5 idées qui t'ont le plus marqué
2. Une citation que tu veux retenir mot pour mot
3. Ce que tu vas faire différemment après cette lecture
```

Sur la base des réponses, générer :

### Note littéraire (format Notion)

```
# [Titre] — [Auteur]
Date de lecture : [date]
Lien avec : [projet ou objectif de Njaho]

## Idées clés
- [Idée 1]
- [Idée 2]
- [Idée 3]

## Citation retenue
> [Citation]

## Ce que je vais changer
[Action concrète]

## Concepts à développer dans le Garden
- [Concept 1]
- [Concept 2]
```

---

## Phase 4 : Concepts pour le Garden Notion

Identifier les concepts intemporels extraits du livre et les formuler pour le Garden :

```
CONCEPTS À AJOUTER AU GARDEN NOTION

[Concept 1] — [Définition en 2 lignes — lien avec la tradition Congo / géo-math / supervision si applicable]
[Concept 2] — [Définition]
```

---

## Phase 5 : Flashcards de mémorisation

Générer des flashcards au format Question / Réponse :

```
FLASHCARDS — [Titre du livre]

Q : [Question sur l'idée clé 1]
R : [Réponse concise]

Q : [Question sur l'idée clé 2]
R : [Réponse concise]

Q : [Question sur la citation]
R : [Citation complète]
```

Proposer d'enregistrer les flashcards dans `context/import/flashcards-[titre].md`.

---

## Phase 6 : Enregistrement et suivi

Créer automatiquement le fichier `context/import/livre-[titre-slug].md` avec :
- La note littéraire complète
- Les concepts pour le Garden
- Les flashcards
- La date de lecture et le lien avec les objectifs

Ajouter une entrée dans `context/HISTORY.md` :
```
## [date] — Livre digéré
- Titre : [Titre] — [Auteur]
- Idées clés retenues : [synthèse]
- Action générée : [ce que Njaho va changer]
- Concepts ajoutés au Garden : [liste]
```

---

## Règles

- Toujours relier le livre à un projet ou objectif concret de Njaho
- Les flashcards doivent être courtes : max 1 ligne question, max 2 lignes réponse
- Si le livre touche aux civilisations africaines, tradition Congo ou spiritualité : enrichir les concepts Garden avec le vocabulaire initiatique de Njaho
- Suggérer Readwise Reader systématiquement si l'ePub est disponible
- Rappeler que l'objectif est la vitesse et la rétention, pas la lecture exhaustive
