# Commande /site

> Pilotage de la masterisation du site njaho.com (WordPress sur Hostinger).
> Audit, refonte, SEO, sécurité, contenu.

---

## Modes disponibles

Quand Njaho tape `/site`, proposer :

```
Site njaho.com — que veux-tu faire ?

1. /site audit     → Lancer l'audit technique et analyser les résultats
2. /site plan      → Revoir le plan de masterisation et choisir le chantier du jour
3. /site refonte   → Travailler l'arborescence, le design et l'UX
4. /site seo       → Titres, métas, structure, indexation, contenu
5. /site secu      → Mises à jour, sauvegardes, durcissement
6. /site contenu   → Rédiger ou réécrire une page
```

Document de référence : `context/import/njaho-site-masterisation.md`.
Rapports d'audit : `reports/site-audit-*/`.

---

## Mode 1 : /site audit

### Étape 1 — Collecte

Lancer le script de collecte (lecture seule, ne modifie rien sur le site) :

```bash
./scripts/audit-wordpress.sh https://njaho.com
```

Il écrit `reports/site-audit-njaho.com-<date>/RAPPORT.md` et les données brutes
dans `raw/`.

Si le script échoue (pas de réseau vers le domaine, cas des sessions Claude Code
sur le web), demander à Njaho de le lancer depuis son poste, ou de fournir :
- le HTML de la page d'accueil (clic droit, Afficher le code source, tout copier)
- une capture de Hostinger > WordPress > Plugins et > Thèmes
- un rapport PageSpeed Insights de njaho.com

### Étape 2 — Compléter avec ce que le script ne voit pas

Ces informations ne sont pas visibles depuis l'extérieur. Les demander à Njaho :

```
Quelques infos que je ne peux pas voir depuis l'extérieur :

1. Version de WordPress et version de PHP (Hostinger > Aperçu du site)
2. Liste complète des plugins actifs + ceux désactivés
3. Sauvegardes : automatiques chez Hostinger ? Fréquence ? Déjà testé une restauration ?
4. Un environnement de préproduction (staging) existe-t-il ?
5. Trafic mensuel actuel (Google Analytics ou Search Console, même approximatif)
6. Le site vend-il quelque chose aujourd'hui (WooCommerce, liens NFT, livres) ?
```

### Étape 3 — Analyse

Lire `RAPPORT.md` et produire un diagnostic structuré :

```
DIAGNOSTIC njaho.com — [date]

État général : [Sain / À consolider / Critique]

BLOQUANT (à traiter cette semaine)
- [Constat] → [Impact concret] → [Action]

IMPORTANT (à traiter ce mois)
- [Constat] → [Impact concret] → [Action]

CONFORT (quand le reste est fait)
- [Constat] → [Action]

Trois chiffres à retenir :
- Score performance mobile : X/100
- Poids de la page d'accueil : X Ko
- Nombre de plugins actifs : X
```

Règles d'analyse :
- Toujours relier un constat technique à une conséquence concrète (visiteur qui
  part, page mal indexée, risque de piratage). Pas de constat sans conséquence.
- Ne jamais recommander plus de 3 actions bloquantes. Au-delà, ce n'est plus un
  plan, c'est une liste de courses.
- Un plugin non utilisé est une faille et un ralentissement. Toujours le signaler.

### Étape 4 — Enregistrer

Écrire le diagnostic dans le dossier d'audit du jour, sous
`DIAGNOSTIC.md`, et mettre à jour la section "État courant" de
`context/import/njaho-site-masterisation.md`.

---

## Mode 2 : /site plan

Relire `context/import/njaho-site-masterisation.md`, afficher où en est chaque
chantier, et proposer le prochain lot de travail réalisable en une session
d'une à deux heures. Un seul chantier à la fois.

Terminer en demandant :
```
On attaque [chantier] maintenant, ou tu préfères autre chose ?
```

---

## Mode 3 : /site refonte

Avant toute proposition de design, verrouiller le positionnement :

```
Question structurante avant de dessiner quoi que ce soit :

njaho.com, c'est le site de qui ?

A. L'artiste peintre uniquement (Congo/Soleil, série géo-mathématique, NFT)
B. L'auteur-chercheur (livres, cheminement initiatique, articles)
C. Le personnage complet (artiste + auteur + ingénieur + association)

A et B se vendent bien seuls. C dilue le message sauf si l'arborescence
sépare clairement les univers.
```

Puis, dans l'ordre :
1. Arborescence cible (pages, profondeur maximale 2 niveaux)
2. Parcours du visiteur type (qui arrive, d'où, pour faire quoi)
3. Contenu de la page d'accueil, bloc par bloc
4. Direction artistique (le site d'un peintre doit laisser respirer les oeuvres :
   fond neutre, images en grand, texte discret)
5. Choix technique du thème

Ne jamais proposer un thème ou un plugin avant d'avoir tranché 1 à 3.

---

## Mode 4 : /site seo

Travailler dans cet ordre, jamais dans un autre :
1. Le site est-il indexable (robots.txt, balise noindex, sitemap soumis dans la
   Search Console)
2. Une page = une intention de recherche. Lister les pages et l'intention visée.
3. Titre et méta description de chaque page (55 à 60 caractères, 150 à 155)
4. Un seul H1 par page, hiérarchie H2/H3 cohérente
5. Textes alternatifs des images (essentiel pour un site d'oeuvres, c'est aussi
   de l'accessibilité)
6. Maillage interne entre les pages
7. Données structurées : Person, VisualArtwork, Book selon les pages

Rappel : sur un site d'artiste, la recherche par image et l'accessibilité
comptent autant que les mots-clés. Les alt text ne sont pas une case à cocher.

---

## Mode 5 : /site secu

Ordre non négociable :
1. **Sauvegarde complète et vérifiée AVANT toute mise à jour.** Fichiers plus
   base de données, téléchargée en local, pas seulement chez l'hébergeur.
2. Mises à jour sur l'environnement de préproduction d'abord si disponible
3. Coeur WordPress, puis extensions, puis thème, une catégorie à la fois
4. Vérifier le site après chaque lot
5. Supprimer (pas seulement désactiver) les extensions et thèmes inutilisés
6. Version de PHP à jour côté Hostinger
7. Comptes utilisateurs : supprimer les inactifs, aucun compte nommé "admin",
   authentification à deux facteurs sur les comptes administrateurs
8. Fermer xmlrpc.php et l'énumération des utilisateurs si exposés

Ne jamais lancer une mise à jour sans sauvegarde vérifiée. Si Njaho dit qu'il
n'a pas de sauvegarde récente, s'arrêter là et la faire.

---

## Mode 6 : /site contenu

Demander quelle page, puis :
1. Objectif de la page (que doit faire le visiteur en sortant)
2. À qui elle parle (collectionneur, lecteur, curieux, journaliste)
3. Structure en blocs
4. Rédaction

Style d'écriture pour ce site : phrases courtes, pas de jargon spirituel
hermétique en page d'accueil, une seule idée par paragraphe. L'oeuvre parle,
le texte accompagne. Pas de tirets longs.

---

## Règles générales

- Ne jamais modifier le site en production sans validation explicite de Njaho
- Ne jamais inventer un constat technique : si la donnée n'est pas dans le
  rapport d'audit, la demander
- Une session = un chantier = un résultat visible
- Après chaque session, mettre à jour la section "Journal" du plan de
  masterisation
