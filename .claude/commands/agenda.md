# Commande /agenda

> Planification de la semaine de Njaho sur toutes ses casquettes.

## Ce que tu dois faire

### Étape 1 : Charger le contexte

Lis `context/CONTEXT.md` pour charger :
- Les projets actifs en cours
- Les objectifs court terme
- Les casquettes actives (Ingénieur, Entrepreneur, Artiste, Chercheur, Père)

Lis `context/HISTORY.md` pour identifier :
- Les actions reportées des sessions précédentes
- Les décisions récentes qui génèrent des tâches

### Étape 2 : Demander les contraintes de la semaine

```
Planifions ta semaine.

Deux questions rapides :

1. Quels sont tes créneaux disponibles cette semaine ?
   (Ex : "lundi et mercredi soir libres", "jeudi journée complète", "week-end dispo")

2. Y a-t-il une deadline ou un événement important cette semaine que je dois prioriser ?
```

Attendre les réponses avant de continuer.

### Étape 3 : Générer le plan hebdomadaire

Construire un plan structuré par casquette et par jour.

Format de sortie :

---

**AGENDA SEMAINE DU [date lundi] AU [date dimanche]**

**Priorité absolue de la semaine**
[1 seul élément, le plus critique]

---

**INGÉNIEUR / NOC**
- [ ] [Tâche 1 — durée estimée]
- [ ] [Tâche 2 — durée estimée]
Créneau suggéré : [jour(s)]

**ARTISTE**
- [ ] [Tâche 1 — durée estimée]
- [ ] [Tâche 2 — durée estimée]
Créneau suggéré : [jour(s)]

**CHERCHEUR / LIVRES**
- [ ] [Tâche 1 — durée estimée]
Créneau suggéré : [jour(s)]

**ENTREPRENEUR**
- [ ] [Tâche 1 — durée estimée]
Créneau suggéré : [jour(s)]

**PÈRE / ASSOCIATION**
- [ ] [Tâche 1 — durée estimée]
Créneau suggéré : [jour(s)]

---

**REPORTÉ DE LA SEMAINE PRÉCÉDENTE**
- [ ] [Actions non faites identifiées dans HISTORY.md]

---

**FOCUS DU LUNDI MATIN**
[Une seule action concrète pour démarrer la semaine avec élan]

---

### Étape 4 : Ajustement

Demander :
```
Est-ce que ce plan te convient ? Tu veux déplacer, alléger ou ajouter quelque chose ?
```

Intégrer les ajustements demandés.

### Étape 5 : Enregistrement optionnel

Proposer :
```
Veux-tu que j'enregistre cet agenda dans context/import/agenda-[semaine].md
pour qu'on puisse faire le bilan vendredi avec /done ?
```

Si oui, créer le fichier `context/import/agenda-AAAA-Wnn.md` avec le plan.

---

## Règles

- Maximum 3 tâches par casquette pour rester réaliste
- Toujours identifier UNE priorité absolue, pas plusieurs
- Ne pas surcharger le planning : mieux vaut 5 tâches tenues que 15 abandonnées
- Prendre en compte les créneaux familiaux et personnels comme des contraintes non négociables
- Si HISTORY.md contient des tâches reportées plusieurs semaines de suite, le signaler explicitement
- Pas de tirets longs dans les réponses
