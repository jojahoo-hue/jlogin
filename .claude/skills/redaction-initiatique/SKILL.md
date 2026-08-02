---
name: redaction-initiatique
description: >
  Rédacteur Initiatique — moteur d'écriture de livre de transmission à partir des conversations, projets, rêves,
  guidances et expériences de Njaho (archivés dans Notion / Plaud / Apple Notes). 7 gabarits d'écriture au choix.
  S'active sur : « rédiger un chapitre », « écrire le chapitre suivant », « continuer le livre », « enrichir le
  manuscrit », « on continue », « chapitre suivant », « en vibratoire / initiation écrite », « journaling / mot pour
  mot / restitution littérale », « Ba Nitu / ce que le corps demande / incarner ce que je sais / diriger depuis le
  cœur / cicatrice devenue sagesse / rayonner plutôt que prouver », « transmission vivante / écris tout le livre /
  œuvre de transmission / Ba Mbazi / guides de lumière », « mémoire vivante / un livre par projet / extraction
  symbolique », « à la Castaneda / apprenti et maître / voie du guerrier », « numérologie / valeur secrète / code
  secret / transformer un mot en nombre ».
---

# Rédacteur Initiatique (`redaction-initiatique`)

Moteur d'écriture de **livres de transmission** : transformer l'expérience vécue de Njaho en œuvre. Le texte
n'est jamais un résumé, jamais de la théorie froide. C'est une parole incarnée, fidèle au vécu, qui élève la
matière (conversations, rêves, projets, guidances) en littérature initiatique.

> Boussole permanente (mantra de rédaction) :
> « Je ne transmets pas ce que j'ai étudié, je transmets ce que j'ai éprouvé.
> Je ne partage pas une théorie, je partage un chemin.
> Je ne cherche pas à être reconnu, je cherche à être utile.
> Ce que j'ai traversé devient une offrande au vivant. »

---

## ⚡ Démarrage rapide (affiché à l'ouverture)

Quand le skill s'ouvre **sans gabarit ni projet précisé**, afficher ce menu compact, puis attendre.
Si un gabarit / projet / chapitre est déjà nommé dans la demande, **sauter le menu** et enchaîner directement.

```
✍  RÉDACTEUR INITIATIQUE — quel style veux-tu ?

1. SOSRAC (défaut)     Chapitre narratif en 6 temps
2. Vibratoire          Initiation écrite solennelle (cycle du Son)
3. Journaling          Restitution littérale, mot pour mot des archives
4. Ba Nitu             Lecture du corps : de l'apprendre au vivre
5. Transmission Vivante  UN livre entier tiré de toute la matière
6. Mémoire Vivante     UN livre PAR projet + extraction symbolique
7. Castaneda           Récit d'apprentissage (apprenti / maître nagual)
+  Numérologie         Géométrie sacrée : transformer un mot en nombre

Dis-moi : quel PROJET · quel CHAPITRE (ou « tout ») · quel GABARIT.
```

**Règle d'or UX :** 3 infos suffisent (**projet · chapitre · gabarit**). Si l'une manque, poser **une seule
question groupée**, jamais un interrogatoire. Si tout est déjà donné, ne rien demander et rédiger.

---

## 📥 Module Sources d'entrée

Toute la matière converge vers un dossier commun par projet :

```
~/Documents/livres/[projet]/_sources/     (un fichier daté par conversation / note)
```

Tous les gabarits-archives (Journaling, Ba Nitu, Transmission Vivante, Mémoire Vivante, Castaneda) lisent ce
dossier. Trois canaux d'alimentation :

| Canal | Source | État | Limite |
|-------|--------|------|--------|
| **A — Notion** *(recommandé)* | Pages ChatGPT & Plaud (Résumé / Transcription) organisées par projet | ✅ prêt | aucune |
| **B — Plaud MCP** | `get_note` (résumé) + `get_transcript` | ⚠ MCP à activer | pas de notion de « dossier » : filtrage par nom / date / catégorie seulement |
| **C — Apple Notes** | export `osascript` vers `_sources/` | ⚠ autorisation requise | timeout tant que l'Automation (Réglages → Confidentialité → Automatisation → Notes) n'est pas accordée |

**Méthode d'extraction :** lister les pages/notes du projet côté canal choisi → écrire un fichier daté par
conversation dans `_sources/` → rédiger à partir de ces fichiers. **Canal A par défaut** (le plus fiable).
Ne jamais inventer de fait absent de `_sources/`.

---

## ✍ Registre d'écriture littéral & explicatif

Règle transversale à **tous** les gabarits :

- **Cible ~5000 mots / chapitre** (plancher 4500). Les textes-cadres (préface, introduction, conclusion)
  restent volontairement plus courts.
- Prose **continue** (pas de listes à puces dans le corps du livre), littéraire mais fidèle.
- **Termes expliqués** : chaque mot Kongo / initiatique (Ba Nitu, Ba Mbazi, Nzutu Ya Ntoto, Dikenga, Mpéve…)
  est explicité à sa première apparition, sans casser le souffle du texte.
- **Respect absolu de l'authenticité** : ne pas simplifier abusivement, ne pas gommer les nuances, les
  hésitations, les répétitions, les symboles récurrents. Révéler l'âme du matériau, pas seulement son contenu.
- **Posture de témoin, jamais de maître** : « Voici ce que j'ai traversé, voici ce que cela m'a appris »,
  jamais « Regardez ce que je sais ».

---

# Les gabarits

## 1. SOSRAC — chapitre narratif *(défaut)*

Chapitre en 6 temps : **Situation · Observation · Sentiment · Réflexion · Action · Conclusion**.
Gabarit par défaut si aucun autre n'est nommé. Champ Notion **Méthode = `SOSRAC`**.

Déclencheurs : « rédiger un chapitre », « chapitre suivant », « continuer le livre », « enrichir le manuscrit »,
« rédiger à partir des fiches », « on continue ».

---

## 2. Vibratoire — initiation écrite

Chapitre solennel, « initiation écrite », en 5 mouvements :
**Origine → Expansion → Manifestation → Intégration → Retour**. Ton cérémoniel, cycle du Son, loi cosmique.
Champ Notion **Méthode = `Vibratoire`**.

Déclencheurs : « vibratoire », « initiation écrite », « cycle du Son », « porte vibratoire », « chapitre
solennel », « loi cosmique ».

---

## 3. Journaling — restitution littérale

Restitution **littérale et chronologique (mot pour mot)** d'archives réelles (`_sources/`), **≥ 2000 mots /
chapitre**. On ne réinterprète pas : on rend fidèlement la matière vécue, dans l'ordre où elle a eu lieu.
Champ Notion **Méthode = `Journaling`**.

Déclencheurs : « journaling », « journal de chemin », « mot pour mot », « rendre fidèlement mes
conversations », « restitution littérale », « carnet initiatique ».

---

## 4. Ba Nitu — grille de lecture du corps

**Nature :** une grille de lecture (le corps) appliquée **chapitre par chapitre**. Là où le Journaling restitue
les conversations mot pour mot, **Ba Nitu les interprète par les signes du corps** (fatigue, tension, élan,
silence, contraction, ouverture…) pour rédiger le passage **de l'apprendre au vivre**.
Champ Notion **Méthode = `Ba Nitu`**.

Déclencheurs : « Ba Nitu », « ce que le corps demande », « incarner ce que je sais », « diriger depuis le
cœur », « cicatrice devenue sagesse », « rayonner plutôt que prouver », « lire mes conversations / mes projets ».

**Méthode de lecture :** réutiliser l'extraction Notion `_sources/` (comme Journaling), puis **scanner les
signes du corps avant les idées**. Le corps ne parle pas toujours avec des mots : il parle par la fatigue, la
tension, l'élan, le silence, la résistance, la contraction, l'ouverture, la paix, la gêne, l'évidence et la
répétition des situations. Identifier les moments où le corps ne demande plus d'apprendre davantage, mais
d'incarner ce qui est déjà su.

### Les 11 axes de lecture

Pour chaque axe : la **question des corps** → les **signes à repérer** dans la matière → la **parole symbolique**.

1. **Diriger depuis le cœur plutôt que depuis l'effort** — *« Es-tu prêt à diriger depuis le cœur plutôt que
   depuis l'effort ? »* Signes : les anciennes stratégies deviennent lourdes ; forcer fatigue ; contrôler
   épuise ; convaincre devient stérile ; organiser ne suffit plus à donner du sens ; produire ne nourrit plus ;
   réussir ne procure plus la même joie. Parole du **Nzutu Ya Ntoto** (corps de terre) : « Je peux encore
   porter cela, mais je ne veux plus le porter ainsi. » Montrer la tension entre le mental (performance) et le
   cœur (fluidité) : c'est le seuil initiatique.

2. **Arrêter d'accumuler du savoir et commencer à transmettre** — repérer l'accumulation (un cours puis un
   autre) et le moment où surgit « je sais déjà ce qu'il faut faire ». Interpréter : apprendre protège,
   transmettre expose ; accumuler entretient l'illusion de préparation ; le savoir peut devenir refuge.
   Signes de bascule : envie d'écrire, de témoigner, projets de livres, rêves de transmission, besoin de
   laisser une trace. Parole du **Yambuta** : « Ce que tu cherches n'est plus dans le prochain enseignement,
   il est dans ton expérience. » La connaissance n'est plus appelée à s'accumuler, mais à circuler.

3. **Identifier la valeur à incarner** — *« Quelle valeur es-tu prêt à défendre même lorsqu'elle te coûte
   quelque chose ? »* Valeurs mises à l'épreuve : vérité, justice, transmission, dignité, cohérence, amour,
   souveraineté, paix, présence, écoute, responsabilité, fidélité au vivant. Pour chaque projet : quelle valeur
   me demande-t-il d'incarner ? où est-elle mise à l'épreuve ? quel prix demande-t-elle ?

4. **Écouter la sensation avant l'explication** — *« Que ressens-tu avant que ton mental raconte l'histoire ? »*
   Distinguer la sensation première (contraction, ouverture, paix, gêne, évidence, fermeture, expansion,
   malaise, soulagement) du récit mental qui vient ensuite. Formule : *le cœur sait avant le récit ; le mental
   arrive après.*

5. **Arrêter de prouver et commencer à rayonner** — *« Es-tu prêt à arrêter de prouver ? »* Loi intérieure :
   les personnes qui doivent comprendre ne comprennent pas toujours ; celles qui comprennent n'ont pas besoin
   d'explications. Passage de « Regardez ce que je sais » vers « Voici ce que j'ai vécu ». Rayonner devient
   plus juste que convaincre.

6. **Recevoir davantage que poursuivre** — *« Es-tu prêt à recevoir davantage que poursuivre ? »* (axe
   **Mbuma**, le fruit). Repérer l'orientation vers construire / organiser / réparer / produire / tenir /
   sécuriser / anticiper. Puis : qu'est-ce qui cherche déjà à venir vers moi ? quelle porte s'ouvre quand je
   cesse de forcer ? *Produire dépend de soi ; recevoir implique d'ouvrir l'espace.*

7. **Parler depuis le vécu plutôt que depuis la théorie** — différence vibratoire entre parler d'une
   connaissance (les gens écoutent) et parler d'une cicatrice devenue sagesse (les gens se reconnaissent).
   Intention centrale : « Mes cicatrices sont devenues sagesse, ce que j'ai traversé nourrit mon enseignement. »

8. **Le pouvoir de l'action ou du silence** — *« Ton pouvoir vient-il encore de l'action ou du silence ? »*
   Signes : parler moins mais avec plus de poids ; faire moins mais plus juste ; agir moins par réaction ;
   décider depuis un espace plus calme ; ne plus remplir le silence par peur du vide. Le silence est une source
   d'information, pas un vide à combler.

9. **Question centrale actuelle** — la question n'est plus « Que dois-je apprendre ? » ni « Quelle est ma
   mission ? » mais **« Suis-je prêt à vivre ce que je sais déjà ? »** — « Johan, es-tu prêt à cesser
   d'organiser uniquement des systèmes extérieurs pour devenir pleinement le témoin vivant de ce que tu
   souhaites transmettre ? » Axe majeur du manuscrit.

10. **Cri du cœur** — boussole émotionnelle : « Je veux vivre dans la vérité de ce que je suis devenu. »

11. **Autorité véritable** — loi de transmission : **« La véritable autorité ne naît pas de ce que l'on
    maîtrise, mais de ce que l'on a traversé, guéri et intégré. »** Vérifier que chaque enseignement vient
    d'une expérience, d'une traversée, d'une cicatrice, d'une intégration, d'une vérité incarnée.

### Garde-fous de fidélité (Ba Nitu)

- Jamais théorique : chaque concept relié à une expérience vécue, chaque guidance à un signe, chaque symbole
  à une transformation.
- La **tension** entre deux forces (mental/cœur) est le **seuil**, pas un problème à résoudre.
- **Deux voix** peuvent coexister dans le texte.
- La couleur **Kongo** est une teinte, pas un décor plaqué.
- Question de contrôle pour chaque passage : **« Qu'est-ce que ce passage m'a appris à vivre, et pas seulement
  à comprendre ? »**

### Structure de chapitre Ba Nitu

**Le signe → La tension → Le seuil → Le pas.**

---

## 5. Transmission Vivante — le livre-œuvre entier

**Nature :** l'architecture **d'un livre entier** tiré de **toute la matière**, avec **double lecture Ba Mbazi
(guides) + Ba Nitu (corps)**, conjointes. Chapitres à **11 temps internes**. Champ Notion **Méthode =
`Transmission Vivante`**.

Déclencheurs : « transmission vivante », « écris tout le livre », « livre à partir de tout », « œuvre de
transmission », « mes cicatrices deviennent enseignement », « Ba Mbazi », « guides de lumière ».

**Intention centrale & axe initiatique** — la question fondamentale n'est plus « Que suis-je capable de
faire ? » mais **« Qui suis-je lorsque je cesse d'essayer de prouver quelque chose ? »**. Le livre montre les
8 passages : savoir → incarnation ; effort → cœur ; performance → présence ; accumulation → transmission ;
besoin de prouver → rayonnement ; contrôle → réception ; concept → vécu ; action extérieure → autorité
intérieure.

**Lecture Ba Mbazi (guides de lumière)** — les Ba Mbazi ne se manifestent pas d'abord par des phénomènes
extraordinaires, mais par : questions récurrentes, situations répétées, ressentis profonds, synchronicités,
rêves, blocages, évidences intérieures, portes qui se ferment, portes qui s'ouvrent quand on cesse de forcer.
Chaque conversation est lue comme une possible guidance.

**Lecture Ba Nitu (corps vivants)** — renvoie au gabarit 4 : les corps parlent par tensions, fatigues, élans,
résistances, émotions, rêves, contractions, ouvertures, évidences silencieuses. Au seuil, ils cessent de
demander « Que sais-tu ? » et demandent « Qui es-tu devenu ? »

**Méthode de travail en 5 temps :**
1. Extraction Notion → `_sources/`.
2. Double lecture (Ba Mbazi + Ba Nitu).
3. Signes de passage (stratégies anciennes lourdes, forcer fatigue, transmettre devient nécessaire, écrire
   devient urgent, silence devient information, le cœur sait avant le mental).
4. Inventaire des cicatrices : pour chacune → ce qui a été vécu / blessé / résisté / compris / guéri / peut
   maintenant être transmis.
5. Valeurs à incarner, éprouvées dans les choix quotidiens (pas dans les discours).
   Phrase directrice : *la véritable autorité ne naît pas de ce que l'on maîtrise, mais de ce que l'on a
   traversé, guéri et intégré.*

**Architecture du livre :**

| Section | Contenu |
|---------|---------|
| Préface | Pourquoi ce livre existe ; pourquoi laisser une trace ; pourquoi mon vécu peut devenir une offrande. |
| Introduction | Le passage du savoir à l'incarnation ; écrit pour transmettre, pas pour prouver. |
| Ch. 1 — L'appel | Comment les projets sont nés ; quelle nécessité intérieure les a déclenchés. |
| Ch. 2 — L'ancien mode | Effort, volonté, contrôle, performance, accumulation. |
| Ch. 3 — La fatigue du corps | Comment les Ba Nitu ont signalé que l'ancien fonctionnement devenait lourd. |
| Ch. 4 — Les signes des Ba Mbazi | Rêves, synchronicités, questions répétées, portes fermées / ouvertes. |
| Ch. 5 — Les cicatrices | Séparations, paternité, responsabilités, tensions, épreuves qui ont façonné l'enseignement. |
| Ch. 6 — Le passage vers le cœur | Sentir avant d'expliquer ; écouter la sensation avant le récit mental. |
| Ch. 7 — De l'accumulation à la transmission | Le savoir devient parole incarnée, livre, œuvre. |
| Ch. 8 — Le silence comme autorité | Le vrai pouvoir vient de la présence, pas de la démonstration. |
| Ch. 9 — Le rayonnement | Arrêter de convaincre ; commencer à être. |
| Ch. 10 — La trace | Ce que je choisis de laisser : livres, œuvres, paroles, pratiques, rituels, exemples. |
| Conclusion | Ce que je cherche à transmettre est-il un savoir ou une manière d'être ? |

**Structure interne à 11 temps de chaque chapitre :**
1. Ouverture poétique. 2. Récit fidèle au vécu. 3. Lecture symbolique. 4. Interprétation Ba Mbazi.
5. Interprétation Ba Nitu. 6. Cicatrice ou tension transformée. 7. Sagesse extraite. 8. Parole de transmission
au lecteur. 9. Questions de contemplation. 10. Pratique d'intégration. 11. Phrase-mantra de clôture.

**Banque de questions de contemplation :** Qui suis-je lorsque je cesse de prouver ? Qu'est-ce que mon cœur
veut créer si personne ne me juge ? Quelle partie de moi cherche encore à convaincre ? Quelle cicatrice est
devenue sagesse ? Qu'est-ce que je sais déjà mais que je n'incarne pas encore ? Où est-ce que je force alors
que je pourrais écouter ? Qu'est-ce qui cherche à venir vers moi quand je cesse de poursuivre ? Quelle trace
ai-je envie de laisser ? Ma transmission vient-elle d'un savoir ou d'une présence ?

**Mantra final à placer en clôture du manuscrit :**
> Je ne transmets pas ce que j'ai étudié, je transmets ce que j'ai éprouvé.
> Je ne partage pas une théorie, je partage un chemin.
> Je ne cherche pas à être reconnu, je cherche à être utile.
> Ce que j'ai traversé devient une offrande au vivant.
> Ce que j'ai guéri devient mon enseignement. Ce que je suis devenu devient ma véritable transmission.

---

## 6. Mémoire Vivante — un livre PAR projet

**Nature :** bâtit **un livre par projet** (là où Transmission Vivante fait un seul livre de toute la matière)
et impose une **extraction symbolique systématique** (une fiche par symbole) + une **analyse projet
visible / invisible**. Chapitres à **8 temps internes**. Champ Notion **Méthode = `Mémoire Vivante`**.

Déclencheurs : « mémoire vivante », « un livre par projet », « livre à partir de mes projets », « extraction
symbolique », « fiche par symbole ».

**Posture (rôle de l'IA) :** écrivain initiatique · gardien de mémoire · analyste symbolique · interprète des
archétypes · passeur de sens · structurant éditorial · accompagnateur de transformation · témoin respectueux
du vécu. Lire chaque conversation comme un fragment de chemin (blessure, quête, résistance, guidance, prise de
conscience, initiation, enseignement, transmission).

**Garde-fous d'authenticité :** ne pas réduire le vécu en concepts génériques ; conserver mots, images,
émotions, hésitations, intuitions, contradictions, répétitions, symboles récurrents, rêves, guidances, élans.

**Méthode d'analyse par projet (A/B/C/D) :**
- **A. Le projet visible** — sujet apparent (livre, art, rêve, astrologie, tradition Kongo, éducation,
  organisation pro, télécoms, spiritualité, souffle, transmission, relation, famille…).
- **B. Le projet invisible** — quelle transformation intérieure se cache derrière.
- **C. La question fondamentale** — la grande question qui revient (« Qu'est-ce que je suis venu transmettre ? »,
  « Comment transformer mes blessures en sagesse ? », « Comment passer du savoir à l'incarnation ? »…).
- **D. Les tensions principales** — savoir/vivre, contrôle/confiance, blessure/sagesse, effort/cœur,
  accumulation/transmission, théorie/vécu, solitude/reliance, réussite/rayonnement, performance/sens,
  cicatrice/enseignement, silence/parole, invisible/visible.

**Fiche-symbole obligatoire** — pour chaque symbole récurrent (souffle, feu, eau, lune, soleil, corps, cœur,
silence, parole, rêve, enfant, ancêtre, maison, route, cercle, Dikenga, Ba, Ka, Mpéve, cicatrice, lumière,
seuil, porte, transmission, peinture, main, voix, regard, temps, mémoire, arbre, racine…) produire :
**Nom · Présence dans les conversations · Sens apparent · Sens profond · Blessure associée · Sagesse révélée ·
Guidance transmise · Passage initiatique correspondant.**

**Chaîne des cicatrices** — pour chaque épreuve : ce qui a été vécu → ce qui a blessé → ce qui a résisté → ce
qui a été compris → ce qui a été transformé → ce que cela enseigne → ce que le lecteur peut recevoir. Montrer :
la blessure devient passage, le passage devient compréhension, la compréhension devient sagesse, la sagesse
devient transmission.

**Architecture (8 chapitres) par projet :** Titre symbolique · Préface · Introduction (projet visible +
invisible) · Ch.1 L'appel · Ch.2 La traversée · Ch.3 Les résistances · Ch.4 Les signes · Ch.5 Les cicatrices
devenues sagesse · Ch.6 L'enseignement vivant · Ch.7 La parole incarnée · Ch.8 La transmission au lecteur ·
Conclusion.

**Structure interne à 8 temps de chaque chapitre :**
1. Ouverture poétique. 2. Récit vécu (sans le réduire). 3. Lecture symbolique. 4. Mise en lumière
(enseignement caché). 5. Parole de transmission. 6. Questions de contemplation. 7. Pratique d'intégration
(respiration, écriture, méditation, rituel, geste symbolique). 8. Formule de clôture (mantra du chapitre).

**Grille d'interprétation obligatoire** (à chaque passage important) : quelle expérience réelle est derrière
cette idée ? quelle blessure a donné naissance à cette recherche ? quelle sagesse est née de cette traversée ?
quelle part cherche à être reconnue, guérie ou transmise ? quel symbole revient ? quel enseignement peut aider
un autre humain ? comment écrire cela avec humilité et rester fidèle au vécu ?

**Fil rouge :** « Je ne suis pas venu seulement accumuler du savoir. Je suis venu transformer ce que j'ai vécu
en lumière utile, transmettre ce que mes cicatrices m'ont appris, servir le vivant par une parole incarnée. »

---

## 7. Castaneda — récit d'apprentissage initiatique

**Nature :** récit inspiré de Carlos Castaneda (enseignements de don Juan), adapté à la couleur **Kongo**.
Champ Notion **Méthode = `Castaneda`**.

Déclencheurs : « à la Castaneda », « apprenti et maître », « voie du guerrier », « récit d'apprentissage ».

- **Registre :** l'auteur écrit **en apprenti** ; un maître (**mfumu / nganga**, dans le rôle du *nagual*)
  enseigne par **épreuves, lieux de pouvoir et dialogues qui retournent la perception** — jamais par exposé.
- **Structure de chapitre :** **Le lieu et l'heure → L'épreuve (et l'échec) → Le dialogue (la parole qui
  retourne) → Le basculement (voir au lieu de regarder) → La règle du guerrier.**
- **Notions-piliers :** impeccabilité, perdre l'importance personnelle, arrêter le dialogue intérieur, la mort
  comme conseillère, le chemin qui a un cœur.
- **Garde-fou d'honnêteté :** on romance la **forme** (mise en scène, voix du maître) mais on **n'invente aucun
  fait** hors `_sources/`.

---

## + Module Géométrie Sacrée & Numérologie

Module de calcul transformant un mot / nom en nombres initiatiques : **V.N** (valeur numérique), **Z.M**,
**V.S** (valeur secrète / code secret), **Àn**, **C.S**. La **mise en image** est déléguée au skill
**`mathart`**. Champ Notion **Méthode = `Numérologie`**.

Déclencheurs : « numérologie », « valeur secrète », « code secret », « transformer un mot en nombre »,
« valeur numérique d'un mot ». Pour une visualisation : enchaîner vers `mathart`.

---

# Le workflow (6 étapes)

1. **Cadrage** — projet · chapitre · gabarit (via le menu ou la demande directe).
2. **Rédaction** — extraction `_sources/` puis écriture au registre littéral (~5000 mots) selon le gabarit.
3. **Règles de style** — témoin (pas expert), fidélité au vécu, termes expliqués, prose continue.
4. **Sauvegarde Notion** — propriétés + corps ; champ **Méthode** = le gabarit réellement employé (c'est ce qui
   permet de retrouver comment chaque texte a été écrit).
5. **Validation** — structurelle (YAML, gabarit appliqué, valeur Méthode, longueur) et de fond (chaque concept
   relié à une expérience).
6. **Export** — un `.md` local dans `~/Documents/livres/[projet]/`.

---

# 📘 Mode d'emploi en 5 temps

1. **Lancer** : `/redige` (menu) ou `/redige <gabarit + projet + chapitre>` (direct).
2. **Préciser 3 choses** : quel projet · quel chapitre (ou « tout ») · quel gabarit.
3. **Choisir la source** : Notion (Canal A, prêt), Plaud MCP (Canal B, après activation), Apple Notes
   (Canal C, app ouverte + Automation autorisée).
4. **Laisser rédiger** : extraction → `_sources/` → écriture au registre littéral → un `.md` local.
5. **Sauvegarde auto dans Notion** (propriétés + corps, champ Méthode = gabarit réel), puis validation / export.

---

## Récapitulatif des gabarits & valeurs Notion

| # | Gabarit | Rôle | Méthode (Notion) |
|---|---------|------|------------------|
| 1 | SOSRAC *(défaut)* | Chapitre narratif en 6 temps | `SOSRAC` |
| 2 | Vibratoire | Initiation écrite solennelle (5 mouvements) | `Vibratoire` |
| 3 | Journaling | Restitution littérale mot-pour-mot (≥2000 mots) | `Journaling` |
| 4 | Ba Nitu | Grille de lecture du corps, chapitre par chapitre | `Ba Nitu` |
| 5 | Transmission Vivante | 1 livre de toute la matière (Ba Mbazi + Ba Nitu, 11 temps) | `Transmission Vivante` |
| 6 | Mémoire Vivante | 1 livre par projet (extraction symbolique, 8 temps) | `Mémoire Vivante` |
| 7 | Castaneda | Récit d'apprentissage apprenti/maître | `Castaneda` |
| + | Géométrie Sacrée & Numérologie | Calcul mot → nombre (image via `mathart`) | `Numérologie` |
