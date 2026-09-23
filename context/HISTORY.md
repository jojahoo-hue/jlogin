# HISTORY.md

> Journal de bord évolutif. Mis à jour automatiquement par Claude après chaque session significative.
> Ne pas modifier manuellement. Utiliser `/update` pour déclencher une mise à jour.

---

## 2026-09-23

### Écriture du livre à partir des notes de la RIK GP

- Livre rédigé à partir du corpus de la Rencontre Initiatique Kongo de Guadeloupe (13 au 24 juillet 2026) : 22 comptes rendus et transcriptions du dossier Drive `RIK / RIK Guadeloupe 2026 / RIK Transcription`, et les synthèses Notion du projet `Nza Ngai dia Nzila RIK GP` (12 attitudes de la maîtrise du Muntu, 12 sens du Muntu, semaine d'intégration, takia du jour 1)
- Titre de travail retenu : **LA GRAINE ET LES RACINES**, carnet initiatique, environ 27 700 mots (110 à 140 pages)
- Architecture choisie : les douze attitudes de la maîtrise du Muntu en quatre niveaux comme colonne vertébrale, plutôt que la chronologie des ateliers. Cinquième partie consacrée au retour et à l'intégration, épilogue sur le fait de devenir l'ancêtre de demain
- Pédagogie centrale de cette RIK intégrée au livre : le basculement du cœur vers le ventre, la graine et les racines comme socle de toutes les pratiques
- Décision éditoriale : aucun protocole réservé aux porteurs de sceau n'est publié (cartouches et calculs du Sonosithia, pentagramme, arbre Kassa, flamme noire hors cadre) ; respect de l'interdit sur le thème, l'autel et la date de naissance
- Contenus écartés du manuscrit et tracés dans `livre/NOTES-EDITORIALES.md` : accusations non vérifiables sur des campagnes de stérilisation, stéréotype sur un pouvoir financier communautaire, généralisations dévalorisantes, promesses de guérison de maladies incurables
- Trois thèses de l'enseignement exposées mais discutées dans le texte : la pauvreté comme signe spirituel, la sortie du salariat, la programmation des naissances selon les signes d'incarnation
- Livrables dans `livre/` : manuscrit assemblé, 18 fichiers de chapitres, 4 annexes (lexique, gabarit de takia, tableaux de synthèse, ce qui a été écarté), notes de dépouillement des sources
- Action en attente côté Njaho : remplir les 12 passages `[à enrichir]`, faire relire par Mfumu Nswadi Kimbazi ou un aîné avant publication, valider l'anonymisation des participants, arrêter le titre définitif
- Projet d'écriture de livres (objectif long terme) désormais amorcé sur une matière concrète

---

## 2026-06-06

### Mise à jour de session — Configuration Jarvis et intégration Notion

- Jarvis Starter Kit déployé sur le dépôt `jojahoo-hue/jlogin`, branche `claude/prime-tDwAc`
- Intégration Notion configurée : MCP Notion dans `.claude/settings.json`, commande `/sync-notion`, script Python `scripts/sync-notion.py`
- Contrainte identifiée : le cloud Claude Code bloque `api.notion.com`, la sync Notion doit tourner depuis le Mac local
- Décision retenue : sync Notion via script Python sur Mac puis push git (Option A)
- Action de sécurité en attente : régénérer le token Notion exposé accidentellement dans le chat
- Claude Code (Jarvis) adopté comme assistant principal en remplacement de ChatGPT

---

## 2026-06-06

### Installation initiale du Jarvis

- Workspace personnalisé pour Njaho, basé à Fort-de-France, Martinique
- Profil principal : Mix — Ingénieur / Entrepreneur / Chercheur / Artiste / Père
- Activité : Responsable d'exploitation et formations dans un opérateur télécom, 20 ans d'expertise
- Objectifs court terme identifiés : automatisation du centre de supervision, lancement site artistique, migration ChatGPT vers Claude
- Vision long terme : département de résilience réseau, oeuvre artistique/spirituelle reconnue, livres publiés, association culturelle développée
- Projets actifs au démarrage : digitalisation centre de supervision, série géo-mathématique, série Congo/Soleil, formation énergies élémentaires, écriture de livres, migration ChatGPT vers Claude
- Domaine d'aide prioritaire : apprentissage et formation, lecture efficace, neurosciences appliquées
- Style de communication choisi : mélange selon contexte (direct pour opérationnel, détaillé pour conceptuel)
- Jarvis Starter Kit installé depuis les fichiers uploadés, profil déjà configuré
