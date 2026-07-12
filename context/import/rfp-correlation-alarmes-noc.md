# CCTP — Corrélation d'alarmes et automatisation du déclenchement (NOC)

> Section technique prête à intégrer dans le cahier des charges de consultation
> pour la prestation de supervision réseau. Rédigée à partir de l'architecture
> OCUA existante et des politiques de corrélation en place.
>
> Généré le 2026-07-12. À relire et adapter avant diffusion prestataire.

---

## 1. Objet et périmètre

La présente section définit les exigences relatives à la **corrélation des
alarmes** et à l'**automatisation du déclenchement des incidents** dans le
centre de supervision (NOC) supervisant le réseau mobile et fixe (2G à 5G) sur
le territoire.

Le prestataire retenu opérera sur la plateforme existante **Oracle
Communications Unified Assurance (OCUA)**, intégrée de façon bidirectionnelle
à **ServiceNow**. Il devra maintenir, gouverner et faire évoluer les politiques
de corrélation, sans en dégrader la maturité actuelle.

## 2. Contexte technique existant

| Composant | État |
|---|---|
| Moteur de corrélation | Oracle Unified Assurance Core (RC3 actif) |
| Détection avancée | ML Anomaly Detection, Topology-based RCA |
| Mécanismes d'alarme | Déduplication, auto-clear, suppression, enrichissement, expiration |
| Ticketing | ServiceNow, intégration bidirectionnelle |
| Sources EMS/NMS | Ericsson, ZTE, Huawei, Nokia, PTI (SNMP, Syslog, API REST, fichiers plats) |
| Visualisation | Vision / GIS Map, overlays météo |

**Niveau de maturité de référence à préserver (baseline contractuelle) :**
80% de tickets créés automatiquement, réduction de 60% du volume d'incidents,
MTTR réduit de 40%, temps NOC sur gestion d'alarmes ramené de 55% à 20%.

## 3. Exigences sur les mécanismes de base

Le prestataire garantit le maintien et l'optimisation continue des mécanismes
suivants, avec reporting mensuel de leur efficacité :

- **Déduplication** : suppression des alarmes redondantes issues d'un même objet.
- **Suppression conditionnelle** : masquage des alarmes subordonnées à une panne
  racine identifiée.
- **Auto-clear** : fermeture automatique des tickets à disparition de la condition.
- **Enrichissement** : ajout systématique des métadonnées site, technologie,
  criticité, SLA impacté.
- **Expiration** : purge des alarmes obsolètes selon règles définies.

Objectif quantifié : réduire d'au moins X% le volume d'alarmes brutes présentées
à l'opérateur par rapport au volume collecté (valeur cible à fixer après audit).

## 4. Matrice des politiques de corrélation exigées

Pour chaque famille d'événements critiques, le prestataire configure et maintient
la politique de corrélation, et applique le niveau d'automatisation cible.

| Famille d'événement | Type de corrélation | Niveau d'automatisation cible | Commentaire |
|---|---|---|---|
| Rupture fibre L3 (connectivité internationale) | Topologique | Assisté (ticket auto + notification) | Action correctrice hors périmètre (opérateur tiers) |
| Rupture fibre L2 (site portant plusieurs sites) | Topologique | Assisté | Intervention physique requise, dispatch auto |
| Perte / dégradation BSC/RNC | Causale + topologique | Semi-automatique | Redémarrage de service sur liste blanche validée |
| Perte simultanée de plusieurs sites | Topologique + temporelle | Assisté | Recherche de cause commune énergie/transmission |
| Dégradation multi-cellules + seuil de performance dépassé | Temporelle + performance | Assisté | Corrélation perf/faute, pas d'action auto |
| Site nodal sur batterie / défaut climatisation | Causale (énergie) | **Boucle fermée** | Cascade déterministe, remédiation cadrée (cf. §5) |
| Disruption > 5% d'un service critique (voix/SMS/data) territoire | Agrégation de service | Assisté, escalade prioritaire | Enjeu critique, décision humaine maintenue |

Types de corrélation attendus :
- **Topologique** : regroupement selon la hiérarchie réseau (site parent → sites enfants).
- **Temporelle** : regroupement d'événements concomitants sur une fenêtre définie.
- **Causale** : identification de l'alarme racine et des alarmes conséquentes.
- **Performance / faute** : corrélation d'un franchissement de seuil KPI avec une alarme.

## 5. Exigences sur la boucle fermée (auto-remédiation)

L'auto-remédiation n'est autorisée que sur un périmètre restreint, sous cadre de
sécurité strict. Le prestataire propose et documente, pour chaque action
automatisée :

1. **Liste blanche d'actions** : uniquement des actions déterministes,
   réversibles et à impact réseau maîtrisé (ex. priorisation d'intervention,
   notification automatique QHSE / logistique, redémarrage de service référencé).
2. **Réversibilité** : toute action automatique doit être annulable et tracée.
3. **Garde-fous** : seuil de déclenchement, fenêtre horaire, limite de fréquence,
   interruption manuelle (kill switch) accessible à l'opérateur.
4. **Journalisation** : chaque action automatique génère une trace dans
   ServiceNow avec horodatage, règle déclencheuse, résultat.
5. **Validation en staging** : aucune boucle fermée mise en production sans test
   de basculement validé sur l'environnement de staging.

**Premier périmètre de boucle fermée (énergie).** Scénario prioritaire :
bascule d'un site nodal sur batterie. Corrélation racine énergie → suppression
des alarmes de sites subordonnés → ouverture ticket enrichi → déclenchement
automatique de la procédure de priorisation d'intervention (groupe électrogène,
notification logistique). Aucune action sur les équipements réseau eux-mêmes.

## 6. Intégration ServiceNow

- Ouverture automatique du ticket à partir de l'événement corrélé, enrichi.
- Mise à jour bidirectionnelle en temps réel (aggravation, auto-clear, résolution).
- Conservation systématique de l'ID d'alarme OCUA dans le ticket (traçabilité).
- Surveillance des flux bidirectionnels pour prévenir les désynchronisations.
- Outil d'ouverture manuelle de ticket depuis une alarme, maintenu.

## 7. Indicateurs et critères d'acceptation

Le prestataire s'engage sur les indicateurs suivants, mesurés mensuellement :

| Indicateur | Cible | Seuil de non-conformité |
|---|---|---|
| Taux de tickets créés automatiquement | ≥ 80% | < 75% |
| Taux de corrélation (alarmes corrélées / alarmes brutes) | à fixer après audit | régression vs baseline |
| Taux de faux positifs de corrélation | ≤ X% | > 2× cible |
| MTTR moyen | ≤ baseline -40% | régression vs baseline |
| Temps NOC passé sur gestion d'alarmes | ≤ 20% | > 30% |
| Incidents critiques non détectés en amont | en baisse continue | hausse sur 2 mois consécutifs |

Toute régression durable par rapport à la baseline OCUA constitue un manquement
contractuel.

## 8. Gouvernance et réversibilité

- Les logiques RC3 en place ne sont pas modifiées sans validation formelle du
  donneur d'ordre.
- Cohérence maintenue des seuils de performance et des règles de criticité
  (High / Major / Minor).
- Tout nouveau connecteur, règle ou service validé en staging avant production.
- Continuité de formation des opérateurs sur dashboards, filtres et outils.
- Maintien du modèle de supervision centralisée à écran unique.
- Documentation à jour des politiques de corrélation, remise trimestrielle.

---

### Notes pour Njaho (hors CCTP, à retirer avant diffusion)

- Les valeurs `X%` et "à fixer après audit" sont volontaires : ne chiffre ces
  cibles qu'après l'audit initial de l'existant, sinon tu t'engages à l'aveugle.
- La baseline OCUA (80% / 60% / -40%) est ton meilleur outil de négociation :
  elle interdit au prestataire de dégrader l'acquis.
- Le scénario énergie (§5) est ton unique boucle fermée en phase 1. Tiens bon
  sur ce périmètre restreint, c'est ce qui rend l'automatisation défendable
  sans risque réseau.
