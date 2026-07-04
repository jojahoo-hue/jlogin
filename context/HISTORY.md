# HISTORY.md

> Journal de bord évolutif. Mis à jour automatiquement par Claude après chaque session significative.
> Ne pas modifier manuellement. Utiliser `/update` pour déclencher une mise à jour.

---

## 2026-06-08

### Synchronisation Notion — Archives ChatGPT

- Identification de la base Notion « ChatGPT conversations » (id `2d892f89-4f8c-81f7-89f8-e1fcfcb851cd`), alimentée par l'extension Chrome « ChatGPT Chats Manager » (Save ChatGPT to Notion) depuis le Mac
- `notion-config.json` configuré : source `chatgpt_archives` reliée à la base et à son data source `2d892f89-4f8c-8131-bcc9-000bfd3f3bda`
- Constat : le MCP Notion fonctionne désormais directement depuis le cloud Claude Code (le blocage `api.notion.com` noté le 2026-06-06 n'est plus d'actualité dans cette session)
- Premier sync vers `context/import/notion-chatgpt-archives.md` : index thématique d'environ 34 conversations récentes (dominante Kôngo/spiritualité, développement personnel, apprentissage)
- Limite : la recherche MCP est sémantique et plafonnée, non exhaustive. Script `scripts/sync-notion.py` corrigé pour traiter `chatgpt_archives` comme une base de données (pagination complète + extraits de contenu) pour un export intégral local
- Automatisation : sync incrémental ajouté en étape 0 de la commande `/morning`
- Ajout du mode `/sync-notion --full` : balayage sémantique multi-requêtes (best-effort) pour rattraper les conversations manquées par l'incrémental. Premier passage : index élargi à une centaine de conversations (ajout des familles télécom/pro, rituels, QCM, mémoire absentes au départ)
- Doublons réels détectés dans la base Notion (« Courrier à ZTE programmation » ×3, « Maîtriser mémoire hologène » ×2), à nettoyer côté Notion
- Extraction des projets via le champ `ProjectName` des conversations : 4 projets nommés identifiés (Lead Process O&M, Nza Ngai dia Nzayi, Nza ngai Sono Zi Tiya, Nza Nga dia KiTuni) et ajoutés à CONTEXT.md (échantillon de 8 conversations, non exhaustif)
- Vérification sécurité : aucun token Notion réel présent dans le dépôt (working tree ni historique git) ; `.env` non suivi et gitignored. Régénération du token exposé dans le chat le 2026-06-06 reste recommandée

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
