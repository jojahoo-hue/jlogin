# Skill : recherche-actualites-contextualisees

> Veille intelligente filtrée selon le contexte personnel de Njaho.

## Déclencheurs

Cette skill s'active automatiquement quand Njaho dit :
- "Fais-moi un point sur les actualités"
- "Donne-moi les news du jour"
- "Qu'est-ce qui se passe dans [domaine lié à son contexte]"
- Via la commande `/morning`

## Ce que fait cette skill

1. Lit `context/CONTEXT.md` pour charger les thèmes prioritaires de Njaho
2. Effectue des recherches web ciblées sur ces thèmes
3. Filtre les résultats selon leur pertinence directe avec les projets et objectifs en cours
4. Présente uniquement ce qui est actionnable ou utile pour Njaho aujourd'hui

## Thèmes de veille par défaut (tirés du contexte Njaho)

- **Télécoms et réseau** : automatisation, résilience réseau, IA appliquée aux NOC/SOC, outils de supervision
- **IA et automatisation** : LLM appliqués aux processus métier, Claude, outils no-code/low-code
- **Art numérique et NFT** : marchés NFT, art génératif, crypto DCA, plateformes de vente d'art
- **Civilisations africaines** : égypte ancienne, Soudan, tradition Congo, recherches archéologiques récentes
- **Neurosciences et apprentissage** : lecture rapide, mémoire, acquisition de compétences, formation adulte

## Format de sortie

```
**[Thème]**
[Titre de l'actualité] — [Source] — [Pourquoi c'est pertinent pour Njaho en 1 ligne]
```

## Règles

- Jamais plus de 5 actualités au total
- Toujours expliquer en quoi chaque news est pertinente pour ses projets spécifiques
- Si une recherche ne donne rien d'utile, ne pas remplir avec du bruit : signaler l'absence
