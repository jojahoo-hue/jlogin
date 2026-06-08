# Commande /morning

> Démarre la journée de Njaho avec une veille personnalisée et un focus du jour.

## Ce que tu dois faire

### Étape 0 : Synchronisation Notion automatique

Avant la veille, synchronise les nouvelles conversations ChatGPT depuis Notion :

1. Lis `notion-config.json` à la racine pour récupérer la source `chatgpt_archives` (id de base, data source) et la valeur `last_sync`.
2. Via les outils MCP Notion, récupère dans la base « ChatGPT conversations » les entrées créées ou modifiées depuis `last_sync`.
3. Si de nouvelles conversations existent, ajoute-les à `context/import/notion-chatgpt-archives.md` (ajout incrémental, ne pas écraser l'existant) en respectant le classement thématique du fichier.
4. Mets à jour `last_sync` dans `notion-config.json` avec la date du jour.
5. Garde cette étape silencieuse, sauf une ligne récap dans le point du matin (voir plus bas).
6. Si le MCP Notion est indisponible, signale-le en une ligne et continue quand même la veille. Ne bloque jamais le `/morning` pour un échec de sync.

### Étape 1 : Veille et focus

1. Lis `context/CONTEXT.md` pour charger les projets actifs et objectifs en cours.

2. Utilise la skill `recherche-actualites-contextualisees` pour effectuer une veille ciblée sur :
   - Télécommunications et automatisation réseau (lié au poste)
   - IA et automatisation (lié aux projets de supervision)
   - Art NFT et marchés crypto (lié aux projets entrepreneuriaux)
   - Civilisations africaines, tradition Congo, spiritualité (lié aux recherches)
   - Neurosciences et apprentissage (lié au domaine d'aide prioritaire)

3. Présente le résultat sous cette forme :

---

**Bonjour Njaho. Voici ton point du [jour/date].**

**Sync Notion**

[Une ligne : nombre de nouvelles conversations ChatGPT synchronisées depuis la dernière fois, ou "Aucune nouvelle conversation". Si la sync a échoué, le dire ici.]

**Actualités filtrées pour toi**

[3 à 5 news pertinentes, une ligne chacune avec la source entre parenthèses]

**Focus du jour recommandé**

Sur la base de tes projets actifs, je te suggère de prioriser aujourd'hui : [un projet ou une action concrète, avec une justification en 1 ligne].

**Question du matin**

[Une question courte et directe pour lancer la réflexion sur le focus recommandé]

---

## Règles

- Maximum 5 minutes de lecture, reste concis
- Ne mentionne que des actualités vraiment pertinentes pour les projets de Njaho
- Pas de bruit informationnel, pas de news générales sans lien avec son contexte
- Si tu n'as pas accès à des actualités récentes, dis-le clairement et propose quand même un focus du jour basé sur CONTEXT.md
- La synchronisation Notion (étape 0) ne doit jamais bloquer ni retarder la veille. En cas de doute ou d'échec, une ligne d'info suffit
- Le sync depuis le MCP est incrémental (depuis `last_sync`). Pour un export complet de tout l'historique, c'est `scripts/sync-notion.py` sur le Mac qui fait référence
