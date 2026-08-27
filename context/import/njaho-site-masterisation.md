# Masterisation njaho.com

> Plan directeur de la remise à niveau du site njaho.com (WordPress, Hostinger).
> Créé le 2026-08-27. Mis à jour par Claude via `/site`.

---

## État courant

| Élément | Valeur |
|---|---|
| Domaine | njaho.com |
| Hébergeur | Hostinger |
| CMS | WordPress |
| Dernier audit technique | **non réalisé** (voir ci-dessous) |
| Positionnement du site | **à trancher** (décision D1) |
| Chantier en cours | aucun |

**Aucune donnée technique n'a encore été mesurée sur le site.** Tout ce qui suit
est une méthode et un cadre, pas un diagnostic. Le diagnostic viendra du premier
audit.

### Pourquoi l'audit n'a pas été fait le 2026-08-27

La session Claude Code tournait dans l'environnement distant (claude.ai/code).
La politique réseau de cet environnement bloque les domaines non autorisés :

```
CONNECT njaho.com:443     -> 403 (policy denial)
CONNECT www.njaho.com:443 -> 403
```

Deux façons de débloquer, au choix :
1. Lancer Claude Code depuis le poste local, où il n'y a pas de filtrage.
   C'est l'option retenue.
2. Ajouter njaho.com à la politique d'accès réseau de l'environnement web
   (documentation : code.claude.com/docs/en/claude-code-on-the-web).

---

## Démarrage : l'audit en 5 minutes

Depuis le poste local, dans le dossier du workspace :

```bash
./scripts/audit-wordpress.sh https://njaho.com
```

Le script est en lecture seule. Il ne se connecte pas à l'administration
WordPress, ne modifie rien, ne teste aucune faille de façon intrusive. Il lit
uniquement des pages publiques.

Ce qu'il mesure :

- temps de réponse serveur (TTFB) et temps de chargement total
- poids du HTML et poids des ressources, les 15 plus lourdes listées
- thème actif, extensions visibles côté public, constructeur de page utilisé
- fichiers sensibles exposés (readme.html, xmlrpc.php, liste des utilisateurs
  via l'API REST, fichiers de sauvegarde oubliés)
- en-têtes de sécurité présents ou absents
- présence et type de cache serveur (LiteSpeed chez Hostinger, Cloudflare)
- titre, méta description, canonical, og:image, hiérarchie des titres,
  images sans texte alternatif, nombre de fichiers JS et CSS
- robots.txt, sitemap XML, liste complète des URL publiées
- scores PageSpeed Insights mobile et ordinateur, Core Web Vitals, poids par
  type de ressource, extensions les plus lourdes, images à optimiser
  (analyse produite par `scripts/psi-analyse.py`, dans `PAGESPEED.md`)

Astuce si le domaine est inaccessible depuis la machine : l'API PageSpeed
Insights est un service Google qui va lui-même visiter le site. Elle fonctionne
donc même derrière un filtrage réseau, tant que googleapis.com est joignable.

```bash
curl -sS "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://njaho.com&strategy=mobile&category=performance&category=seo&category=accessibility&category=best-practices" -o psi.json
python3 scripts/psi-analyse.py psi.json
```

Le quota anonyme est vite épuisé et partagé entre tous les appelants. Une clé
gratuite obtenue sur la console Google Cloud (API PageSpeed Insights) supprime
le problème : `export PSI_API_KEY=...`

Puis, dans Claude Code :

```
/site audit
```

Claude lit le rapport, produit le diagnostic priorisé et le range dans le
dossier d'audit du jour.

---

## Décision D1 : à qui parle njaho.com

**C'est la décision qui commande tout le reste.** Design, arborescence, textes,
SEO : rien ne peut être arbitré avant.

Trois scénarios possibles compte tenu du profil (peintre, auteur de deux livres,
chercheur, ingénieur télécom, association culturelle en création) :

### Scénario A — Le site de l'artiste peintre

Cible : collectionneurs, galeries, acheteurs NFT, curieux d'art.

```
Accueil (une oeuvre plein écran + une phrase)
├── Oeuvres
│   ├── Série Congo / Soleil
│   └── Série géo-mathématique
├── Démarche (le sens du travail, la conscience dans la création)
├── NFT / Collectionner
├── Expositions et actualités
└── Contact
```

Avantage : message limpide, référencement facile à cibler, crédibilité auprès
des galeries. Inconvénient : les livres et la recherche n'ont pas leur place,
il faut un second site ou un sous-domaine.

### Scénario B — Le site de l'auteur-chercheur

Cible : lecteurs, personnes en cheminement, organisateurs de conférences.

```
Accueil
├── Livres
├── Écrits / Articles
├── Recherche (tradition Congo, civilisations africaines, conscience)
├── Rencontres et formations
└── Contact
```

Avantage : un blog nourrit le référencement naturel dans la durée, ce qu'une
galerie d'images ne fait pas. Inconvénient : le travail pictural devient
secondaire.

### Scénario C — Le personnage complet

Cible : tout le monde, donc personne en particulier, sauf si l'arborescence
sépare nettement les univers dès l'accueil.

```
Accueil (trois portes clairement distinctes)
├── L'oeuvre        → galerie, séries, NFT
├── Les écrits      → livres, articles, recherche
├── La transmission → association, ateliers nature, prise de rendez-vous
├── À propos
└── Contact
```

Avantage : un seul site à maintenir, une seule identité, cohérent avec un
parcours où l'art, la recherche et la transmission sont le même mouvement.
Inconvénient : c'est le plus difficile à réussir. Un site à trois portes rate
sa cible si la page d'accueil hésite.

**Recommandation :** commencer par A ou C.

A si l'objectif des six prochains mois est de vendre des oeuvres et de lancer
les NFT. C'est ce que dit l'objectif court terme du CONTEXT.md ("lancer le site
web de promotion de ses oeuvres artistiques").

C uniquement si le site doit aussi servir l'association et les livres dès
maintenant, en acceptant une page d'accueil plus exigeante à concevoir.

B seul serait dommage : les tableaux sont l'atout visuel le plus fort, et un
site d'écrivain sans images convertit moins bien pour quelqu'un qui peint.

À noter : l'association culturelle (ateliers nature, soins holistiques, prise de
rendez-vous) mérite à terme son propre site. C'est une autre cible, une autre
promesse, et un module de réservation alourdit un site vitrine d'artiste.

---

## Les quatre chantiers

Ordre imposé. Chaque chantier suppose le précédent terminé.

### Chantier 0 — Filet de sécurité (avant toute chose, 30 min)

Rien ne se touche tant que ce n'est pas fait.

- [ ] Sauvegarde complète : fichiers **et** base de données, téléchargée en local
- [ ] Vérifier que l'archive s'ouvre et que le fichier SQL n'est pas vide
- [ ] Activer les sauvegardes automatiques Hostinger si ce n'est pas déjà fait
- [ ] Créer un environnement de préproduction (Hostinger > WordPress > Staging)
      si le plan d'hébergement le permet
- [ ] Noter les identifiants d'accès au gestionnaire de fichiers et à la base

Une sauvegarde non testée n'est pas une sauvegarde.

### Chantier 1 — Socle technique (sécurité et maintenance, 2 h)

- [ ] Version de PHP à jour côté Hostinger (une version obsolète est lente et
      non corrigée)
- [ ] Mise à jour du coeur WordPress, puis des extensions, puis du thème,
      une catégorie à la fois, avec vérification du site entre chaque lot
- [ ] **Supprimer** les extensions et thèmes inutilisés, ne pas se contenter de
      les désactiver : un fichier présent reste attaquable
- [ ] Objectif : moins de 15 extensions actives. Au-delà, chaque extension
      ajoute du code sur toutes les pages
- [ ] Comptes utilisateurs : supprimer les inactifs, aucun compte nommé "admin",
      mots de passe uniques, double authentification sur les comptes
      administrateurs
- [ ] Fermer ce que l'audit signale comme exposé (readme.html, xmlrpc.php si
      inutilisé, énumération des auteurs via l'API REST)
- [ ] Une extension de sécurité, une seule (jamais deux, elles se gênent) :
      Wordfence ou Solid Security, réglages par défaut suffisants au début
- [ ] Certificat HTTPS valide, redirection systématique de http vers https,
      pas de contenu mixte

### Chantier 2 — Structure et contenu (le plus long, 4 à 8 h)

Dépend de la décision D1.

- [ ] Arborescence cible écrite noir sur blanc, deux niveaux maximum
- [ ] Pour chaque page existante : garder, fusionner, réécrire ou supprimer
- [ ] Redirections 301 pour toute URL supprimée ou déplacée (sinon erreurs 404
      et perte de référencement)
- [ ] Page d'accueil : une promesse en une phrase, une image forte, un seul
      appel à l'action principal
- [ ] Fiches oeuvres : titre, année, technique, dimensions, série, une phrase
      de sens, statut (disponible, vendue, NFT)
- [ ] Page "Démarche" : le texte le plus important du site, celui qui distingue
      un peintre d'un autre
- [ ] Pages livres : couverture, extrait, où l'acheter
- [ ] Mentions légales et politique de confidentialité (obligation légale,
      souvent absente ou périmée)
- [ ] Formulaire de contact fonctionnel et testé (les formulaires cassés sont
      la panne la plus fréquente et la plus invisible)

### Chantier 3 — Performance (2 à 3 h)

Pour un site d'artiste, tout se joue sur les images.

- [ ] Cache serveur activé (LiteSpeed Cache chez Hostinger, gratuit et efficace)
- [ ] Images converties en WebP, redimensionnées à leur taille d'affichage
      réelle. Une photo d'atelier de 4000 px affichée en 800 px, c'est 90 % du
      poids jeté par la fenêtre
- [ ] Chargement différé (lazy load) sur toutes les images sauf celle du haut
      de la page d'accueil
- [ ] Polices hébergées localement plutôt que chargées depuis Google Fonts
      (plus rapide, et conforme au RGPD)
- [ ] Réduire le nombre de fichiers JS et CSS : c'est presque toujours le
      symptôme d'extensions en trop
- [ ] Cible réaliste : score mobile supérieur à 70, LCP sous 2,5 s,
      page d'accueil sous 1,5 Mo au total
- [ ] Mesurer avant et après, sinon on optimise à l'aveugle

### Chantier 4 — Référencement et visibilité (2 h)

- [ ] Une extension de SEO, une seule : Rank Math ou Yoast
- [ ] Titre et méta description propres sur chaque page
- [ ] Un seul H1 par page, hiérarchie cohérente
- [ ] Texte alternatif sur toutes les images d'oeuvres, descriptif et précis :
      c'est ce qui fait remonter les tableaux dans la recherche par images, et
      c'est ce que lisent les personnes non voyantes
- [ ] Sitemap soumis dans la Google Search Console, propriété vérifiée
- [ ] Données structurées : Person pour la page à propos, VisualArtwork pour
      les oeuvres, Book pour les livres
- [ ] Aperçu correct au partage sur les réseaux (og:image, og:title)
- [ ] Google Analytics ou une alternative respectueuse de la vie privée
      (Plausible, Matomo), avec la bannière de consentement qui va avec

---

## Stack recommandée

Sur un site d'artiste, le bon réflexe est de retirer, pas d'ajouter.

| Besoin | Choix recommandé | À éviter |
|---|---|---|
| Thème | Kadence, Blocksy ou GeneratePress (légers, éditeur de blocs natif) | Thèmes ultra-chargés vendus sur les places de marché |
| Mise en page | Éditeur de blocs natif de WordPress | Empiler un constructeur de page en plus du thème |
| Cache | LiteSpeed Cache (inclus chez Hostinger) | Deux extensions de cache en même temps |
| Images | ShortPixel ou Imagify | Téléverser des JPEG de 5 Mo |
| SEO | Rank Math ou Yoast | Les deux ensemble |
| Sécurité | Wordfence ou Solid Security | Les deux ensemble |
| Sauvegarde | Hostinger + UpdraftPlus en second filet | Se fier uniquement à l'hébergeur |
| Formulaire | Fluent Forms ou WPForms Lite | Contact Form 7 laissé sans anti-spam |

Règle simple : une fonction, une extension. Deux extensions qui font la même
chose se neutralisent et cassent le site.

---

## Séquencement proposé

| Semaine | Chantier | Durée | Résultat visible |
|---|---|---|---|
| 1 | Audit + Chantier 0 + décision D1 | 1 h | On sait où on est et où on va |
| 2 | Chantier 1 (socle technique) | 2 h | Site à jour, sauvegardé, propre |
| 3 | Chantier 2 (structure et contenu) | 4 à 8 h | Le site raconte enfin la bonne histoire |
| 4 | Chantiers 3 et 4 (perf et SEO) | 4 h | Site rapide et trouvable |

Faire les chantiers dans l'ordre. Optimiser la performance d'une page qu'on va
réécrire, c'est du travail perdu deux fois.

---

## Journal

### 2026-08-27
- Création du plan de masterisation
- Création du script `scripts/audit-wordpress.sh` (collecte technique en
  lecture seule)
- Création de la commande `/site` (audit, plan, refonte, seo, secu, contenu)
- Audit du site impossible depuis l'environnement distant : domaine bloqué par
  la politique réseau. À lancer depuis le poste local.
