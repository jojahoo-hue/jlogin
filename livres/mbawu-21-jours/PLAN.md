# PLAN — Mbawu, les vingt-et-un jours

> Document de cadrage et d'architecture éditoriale.
> **Statut : ébauche non validée.** Tout ce qui suit est une proposition de contenant,
> pas du contenu. Le contenu viendra des notes du projet Nza Ngai dia Nzayi.

---

## 1. Cadrage éditorial

Cinq décisions à trancher avant d'écrire. Réponses à consigner ici.

| # | Question | Réponse |
|---|----------|---------|
| 1 | À qui s'adresse le livre ? Initiés, grand public, chercheurs, transmission familiale | *à trancher* |
| 2 | Promesse en une phrase : que sait ou vit le lecteur après, qu'il ignorait avant ? | *à trancher* |
| 3 | Régime d'écriture : récit initiatique vécu, enseignement structuré, manuel de pratique, mixte | *à trancher* |
| 4 | Format et longueur : ePub, PDF, Word, auto-édition ou éditeur, nombre de pages visé | *à trancher* |
| 5 | **Périmètre de non-divulgation** : ce qui ne doit pas être écrit, noms à protéger, contenu réservé au cercle | **Tranchée par défaut, voir section 2** |

La question 5 est la plus importante. Une fois tranchée, elle s'applique sans exception à
toute la rédaction, y compris aux exemples et aux notes de bas de page.

---

## 2. Périmètre de non-divulgation

**Statut : réponse par défaut, choisie par Claude à la demande de Njaho, le 2026-09-03.**
Volontairement restrictive. Njaho seul sait ce qu'il a juré et devant qui. Desserrer une
règle plus tard coûte une ligne, reprendre une divulgation ne se fait pas.

### Règle générale : la règle du seuil

Le livre conduit le lecteur jusqu'à la porte et décrit ce que le passage fait à un être.
Il ne remet pas la clé. Autrement dit : le livre dit **ce qui se joue** et **ce que cela
transforme**, jamais **comment l'exécuter seul**.

En cas de doute sur un élément, il sort du livre. Le doute n'est pas arbitré en faveur du
texte.

### Ce qui ne s'écrit pas

1. **Tout ce qui a été transmis sous condition explicite de secret.** Sans exception, et
   sans reformulation habile qui contournerait la lettre de l'engagement.
2. **Le détail opératoire du rite.** Formules et invocations mot pour mot, séquences de
   gestes, noms à prononcer, dosages, matières exactes, horaires liés à l'efficacité du
   rite. Le livre peut dire qu'une parole est prononcée et ce qu'elle ouvre. Il ne la
   donne pas.
3. **Les noms de personnes.** Initiateurs, aînés, membres du cercle, famille. Sauf accord
   écrit de la personne. À défaut, désigner par la fonction : l'aîné, mon initiateur,
   celui qui tenait le feu.
4. **Les lieux précis.** Sanctuaires, concessions familiales, sites, itinéraires,
   coordonnées. Géographie générale seulement.
5. **Le vécu des autres.** Les initiations, les crises, les confidences d'autrui pendant
   les vingt-et-un jours. Njaho témoigne de son propre passage. Les autres n'ont pas
   signé pour être publiés.
6. **Les noms sacrés dont l'énonciation est réglée.** Mentionner leur existence et leur
   fonction, jamais le mot lui-même.
7. **Toute pratique corporelle reproductible sans encadrement.** Jeûnes, plantes,
   privations, veilles. Ni protocole, ni durée, ni posologie. Un lecteur isolé qui
   recopie se met en danger, et l'auteur engage sa responsabilité.

### Ce qui s'écrit sans réserve

- Le récit intérieur : ce que Njaho a traversé, senti, compris, redouté, perdu, reçu
- Le sens, la cosmologie, la fonction des étapes, ce que la tradition vise
- Les effets sur la vie ordinaire, après
- Ce qui est déjà publié dans la littérature ethnographique, **cité comme littérature avec
  sa source**, jamais présenté comme transmission personnelle. Cette distinction protège
  l'engagement : citer un auteur publié n'est pas divulguer ce qu'on a reçu

### Traitement des cas limites

Un élément écarté n'est pas oublié en silence. Il laisse une trace dans le texte de
travail :

```
> [RÉSERVÉ : ce qui se passe à ce moment du septième jour. Njaho tranche.]
```

Ces marqueurs sont recensés en fin de session. Njaho arbitre, un par un. Ce qui reste
réservé disparaît du manuscrit final sans laisser de cicatrice dans la lecture.

### Conséquence matérielle : le dépôt est public

Vérifié le 2026-09-03 : `jojahoo-hue/jlogin` est un dépôt **public**. Tout ce qui y est
commité est lisible par n'importe qui, indexé, forkable, et reste récupérable dans
l'historique même après suppression.

En conséquence, `livres/*/notes-sources/**` est ajouté au `.gitignore`. Les notes brutes
ne partent pas sur GitHub tant que le dépôt n'est pas passé en privé. Cette règle se lève
en supprimant deux lignes du `.gitignore`, une fois le dépôt privé et le tri fait.

---

## 3. Identité du livre

- **Titre de travail :** Mbawu, les vingt-et-un jours
- **Sous-titre :** *à définir*
- **Auteur :** Njaho
- **Projet source :** Nza Ngai dia Nzayi
- **Langue :** français, vocabulaire initiatique kikongo conservé tel quel et explicité en glossaire

---

## 4. Architecture proposée

**Hypothèse de travail, à valider ou à jeter une fois les notes lues.**

La structure la plus évidente est celle que la matière impose déjà : vingt-et-un jours,
donc vingt-et-un chapitres, un par jour. Trois cycles de sept se dégagent naturellement
d'un tel nombre, mais rien dans les notes ne l'a encore confirmé. Si les notes révèlent
un autre découpage, c'est lui qui l'emporte.

```
Ouverture
  Avant-propos          Pourquoi ce livre, pourquoi maintenant
  Seuil                 Ce qu'est Mbawu, ce que sont les vingt-et-un jours
  Comment lire ce livre Mode d'emploi si régime "manuel de pratique"

Corps
  Cycle I    — Jours 1 à 7     [intention du cycle à établir depuis les notes]
  Cycle II   — Jours 8 à 14    [intention du cycle à établir depuis les notes]
  Cycle III  — Jours 15 à 21   [intention du cycle à établir depuis les notes]

Clôture
  Le vingt-et-unième jour et après
  Glossaire
  Sources et transmissions
```

Structure interne proposée pour chaque chapitre de jour, à ajuster après lecture des notes :

1. Le jour et son nom
2. Ce qui se joue (l'enseignement)
3. Le vécu (récit à la première personne, tiré des notes)
4. La pratique (ce que le lecteur fait, si le régime retenu est le manuel)
5. Ce qui reste (une phrase à emporter)

---

## 5. Table de correspondance chapitres / sources

À remplir dès que `notes-sources/` est alimenté. Un chapitre sans source identifiée ne
s'écrit pas.

| Chapitre | Intention | Fichiers sources | Longueur cible | Statut |
|----------|-----------|------------------|----------------|--------|
| *à remplir après import des notes* | | | | |

---

## 6. Trous connus

Liste des sujets que les notes ne couvrent pas et qu'il faudra dicter, retrouver ou
compléter. À alimenter pendant la lecture des sources et pendant la rédaction.

- *aucun identifié à ce stade, les notes ne sont pas encore importées*

---

## 7. Règle de fidélité

Chaque affirmation portant sur la tradition, le rite, les correspondances ou le déroulé
des vingt-et-un jours doit être traçable à un passage précis de `notes-sources/`.

Quand une notion manque, le texte porte un marqueur visible plutôt qu'une invention :

```
> [À COMPLÉTER : quel est le nom du troisième seuil ? Les notes s'arrêtent au deuxième.]
```

Ces marqueurs sont recensés à chaque fin de session et soumis à Njaho.
