# Clause de réversibilité — Prestation de supervision NOC

> Clause à intégrer au contrat du prestataire sortant (ou à activer si elle
> existe déjà) pour garantir la restitution complète de la connaissance et des
> configurations avant la bascule vers le nouveau prestataire.
>
> Généré le 2026-07-12. **Projet de clause à faire valider par le service
> juridique et à adapter au contrat réel.** Ce n'est pas un avis juridique.

---

## Article X — Réversibilité et restitution

### X.1 Objet

En fin de contrat, ou à la demande du donneur d'ordre, le Prestataire sortant
s'engage à assurer une **réversibilité complète** de la prestation de
supervision, permettant au donneur d'ordre ou à un prestataire entrant de
reprendre l'exploitation sans perte de connaissance, de configuration ni de
continuité de service.

### X.2 Périmètre des éléments à restituer

Le Prestataire restitue, dans des **formats ouverts et exploitables** (non
verrouillés par un outil propriétaire), l'ensemble des éléments suivants :

**Plateforme de supervision (OUA/OCUA)**
- Export complet et documenté des **politiques de corrélation RC3** en place.
- Configurations des mécanismes d'alarme : déduplication, suppression
  conditionnelle, auto-clear, enrichissement, expiration, seuils.
- Paramétrage et résultats du module **ML Anomaly Detection**.
- Configuration des dashboards, rapports et vues opérationnelles.

**Topologie et intégrations**
- Modèle de **topologie réseau** complet (RAN, faisceaux hertziens, IP/MPLS) tel
  que configuré dans OUA.
- Configuration des **connecteurs EMS** : Nokia MantaRay (radio), NetNumen (ZTE,
  hertzien), remontées SNMP directes IP/MPLS.
- Configuration de l'intégration **i-ENERGY ZTE** (énergie) vers OUA, si en place.
- Configuration de l'**intégration bidirectionnelle ServiceNow** (mapping des
  champs, workflows).

**Données historiques**
- Historique exploitable des **12 derniers mois** : alarmes, tickets, MTTR,
  taux de corrélation, taux d'automatisation, incidents majeurs.

**Documentation d'exploitation**
- Runbooks et SOPs par technologie.
- Procédures d'exploitation, matrices d'escalade, playbooks de crise.
- Documentation d'architecture à jour.
- Inventaire énergie (parcs batteries, âge, état de santé) et méthode de
  calibration de l'autonomie i-ENERGY.

**Accès et actifs**
- Transfert sécurisé des comptes, accès, licences et identifiants nécessaires.
- Inventaire des actifs et des dépendances tierces (ZTE, éditeurs).

### X.3 Modalités et calendrier

- La réversibilité débute au plus tard **[N] semaines** avant la fin de contrat.
- Le Prestataire fournit un **plan de réversibilité** détaillé sous [X] jours
  après demande.
- Une **période de recouvrement (parallel run)** est assurée, pendant laquelle
  le sortant et l'entrant opèrent conjointement pour garantir la continuité.

### X.4 Transfert de compétences

Le Prestataire assure un **transfert de connaissances** actif : sessions
documentées, accompagnement des équipes entrantes (shadowing), réponses aux
questions techniques pendant la période de recouvrement.

### X.5 Continuité de service

La réversibilité s'effectue **sans interruption ni dégradation** du service de
supervision. La baseline de performance (taux d'automatisation, MTTR, taux de
corrélation constatés) est maintenue jusqu'au transfert effectif.

### X.6 Sécurité et confidentialité des données

- Restitution des données conforme au **RGPD**.
- Restitution puis **destruction certifiée** des données détenues par le
  Prestataire à l'issue du transfert, avec attestation.

### X.7 Recette de réversibilité

Le transfert est validé par une **recette de réversibilité** : le donneur
d'ordre vérifie l'exhaustivité et l'exploitabilité des éléments restitués
(notamment que les politiques de corrélation et la topologie sont réutilisables).
La réversibilité n'est réputée achevée qu'après recette signée.

### X.8 Pénalités

Tout manquement à l'obligation de réversibilité (élément manquant, format
inexploitable, dépassement de délai) donne lieu à **[pénalités à définir]**,
sans préjudice de la continuité de service due.

---

### Notes pour Njaho (à retirer)

- Les `[N]`, `[X]`, `[pénalités]` sont à fixer avec le juridique et selon le
  contrat réel.
- Le point le plus important pour toi, opérationnellement, ce sont **X.2
  (politiques de corrélation + topologie) et le calibrage i-ENERGY**. Ce sont
  exactement les entrées de ta Phase 0. Sans elles, tu repars de zéro.
- Fais-toi confirmer par le juridique si une clause de réversibilité existe
  déjà dans le contrat en cours : si oui, il s'agit de l'activer et de préciser
  le périmètre technique ci-dessus, pas d'en créer une.
- Vérifie la propriété des configurations OUA : selon le contrat, elles
  peuvent appartenir au donneur d'ordre (toi) et non au prestataire. Argument
  fort pour exiger la restitution.
