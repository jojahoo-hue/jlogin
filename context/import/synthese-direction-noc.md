# Automatisation du centre de supervision (NOC)

## Note de synthèse — Direction

> À coller dans Gamma pour génération de présentation. Un titre = une slide.
> Généré le 2026-07-12.

---

## Le constat

Notre NOC est déjà automatisé via Oracle Unified Assurance (corrélation, ML,
ticketing ServiceNow). La performance de référence du déploiement : 80% de
tickets créés automatiquement, 60% d'incidents en moins, MTTR réduit de 40%.

Deux faits nouveaux ouvrent une fenêtre d'action :
- Un gisement d'automatisation reste inexploité (les ~20% de tickets encore manuels).
- Le changement de prestataire de supervision est en cours.

## La vision

Faire passer notre supervision d'un modèle **assisté** à un modèle
**semi-autonome**, où le système corrèle, priorise et déclenche les
interventions, sans jamais agir seul sur les équipements réseau.

Objectif : moins de temps passé sur le bruit d'alarmes, une intervention plus
rapide sur les incidents à fort impact, un NOC recentré sur l'expertise.

## L'approche : prouver avant d'étendre

Nous n'automatisons pas tout en même temps. Séquencement par niveau de risque :

1. **Corrélation d'alarmes** (déjà mature) : optimiser et mesurer.
2. **Escalades** : automatiser le routage des interventions.
3. **Troubleshooting** : en dernier, au compte-goutte, sur actions sûres.

L'automatisation autonome (boucle fermée) est réservée à un seul périmètre en
phase 1 : l'énergie. Périmètre restreint, réversible, zéro risque réseau.

## Le quick win : l'énergie

Quand un site nodal bascule sur batterie, la panne est prévisible. Grâce à la
télémétrie i-ENERGY (temps d'autonomie restant), le système peut :

- corréler l'événement racine et supprimer le bruit d'alarmes conséquent,
- prioriser automatiquement selon l'autonomie réelle du site,
- déclencher le dispatch du groupe électrogène et alerter les équipes.

Résultat attendu : moins de sites perdus par épuisement batterie, un délai
d'intervention réduit, un impact client contenu. Le tout sans action sur le
réseau.

## Le retour attendu

La baseline actuelle (80% auto, -60% incidents, -40% MTTR, -25% de ressources
NOC) devient notre **plancher contractuel** avec le nouveau prestataire : il ne
peut pas dégrader l'acquis. Le gain additionnel vient du gisement manuel
restant et du périmètre énergie.

Note : ces chiffres seront confirmés sur nos propres données lors de l'audit
Phase 0, avant tout engagement chiffré.

## L'urgence à traiter maintenant

Le prestataire sortant détient une connaissance critique (politiques de
corrélation, topologie, calibrage énergie). Sans action, elle part avec lui.

→ Activer une **clause de réversibilité** dans le contrat sortant pour récupérer
ces éléments avant la bascule. C'est la priorité immédiate.

## Ce que je demande

1. **Valider le séquencement** (corrélation → escalades → troubleshooting, boucle
   fermée limitée à l'énergie).
2. **Mandater la Phase 0 d'audit** (4 semaines : baseline réelle, couverture et
   calibrage i-ENERGY, topologie).
3. **Intégrer la clause de réversibilité** au contrat du prestataire sortant, en
   lien avec le juridique.
