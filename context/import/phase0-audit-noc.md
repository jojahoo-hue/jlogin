# Phase 0 — Audit préalable à l'automatisation NOC

> Plan d'audit à mener avant tout déploiement d'automatisation. Objectif :
> mesurer l'existant réel, identifier les manques, produire un go/no-go documenté
> pour la phase 1. Sans cette phase, on automatise à l'aveugle.
>
> Généré le 2026-07-12. Document de travail interne.

---

## 0. Enjeu de timing (à lire en premier)

La supervision est externalisée et tu changes de prestataire. **Une grande
partie des données d'audit ci-dessous est détenue par le prestataire sortant et
par ZTE.** Une fois le sortant parti, cette connaissance disparaît.

→ **Action prioritaire :** inscrire la fourniture de ces éléments d'audit comme
**clause de réversibilité** dans le contrat sortant, et les extraire AVANT la
bascule. C'est ton unique fenêtre pour récupérer les politiques de corrélation,
la topologie et l'historique de performance réels.

## 1. Audit de l'existant OUA / corrélation

| Point à auditer | Question précise | Artefact attendu |
|---|---|---|
| Baseline réelle | Quel est le taux réel de tickets auto, le MTTR, le taux de corrélation sur MES données (pas le chiffre marketing du success story) ? | Extraction OUA 6-12 mois |
| Politiques RC3 | Quelles politiques de corrélation sont configurées, sur quelles familles ? | Export des règles RC3 |
| Gisement manuel | Quelles familles d'alarmes échappent encore à la corrélation (les ~20% manuels) ? | Analyse des tickets créés manuellement |
| Qualité alarmes | Efficacité dédup/suppression, taux de faux positifs de corrélation ? | Rapport qualité alarmes |
| ML Anomaly | Le module ML est-il réellement exploité ou dormant ? Sur quels KPIs ? | Config + résultats ML |

**Point de vigilance :** ne contractualise aucune cible chiffrée dans ton RFP
avant d'avoir mesuré ta vraie baseline ici. Le 80%/60%/-40% du success story est
un chiffre fournisseur, pas forcément ta réalité actuelle.

## 2. Audit i-ENERGY ZTE (le prérequis de la boucle fermée énergie)

| Point à auditer | Question précise | Artefact attendu |
|---|---|---|
| Couverture | Tous les sites nodaux sont-ils équipés et remontés par i-ENERGY ? Lesquels manquent ? | Liste sites nodaux vs sites i-ENERGY |
| Sites non-ZTE | Les sites à alimentation non-ZTE sont-ils couverts autrement, ou aveugles ? | Cartographie énergie par fournisseur |
| Calibration autonomie | Le "remaining backup time" est-il calibré (âge batteries, charge réelle) ou théorique ? | Méthode de calcul i-ENERGY + tests |
| Fiabilité donnée | Fréquence de remontée, taux de valeurs manquantes, latence ? | Échantillon de télémétrie sur 30 j |
| Historique batteries | Âge et état de santé (SOH) des parcs batteries des sites nodaux ? | Inventaire batteries |

**Sans calibration fiable de l'autonomie, le seuil de déclenchement du dispatch
est faux.** C'est le point le plus critique de la phase 0.

## 3. Audit topologie (la base de la corrélation)

| Point à auditer | Question précise | Artefact attendu |
|---|---|---|
| Complétude | La topologie OUA (nodal → sites subordonnés) est-elle à jour et exhaustive ? | Export topologie |
| Liens hertziens | Les dépendances de transport (NetNumen) sont-elles modélisées dans OUA ? | Cartographie liens FH |
| IP/MPLS | Les remontées SNMP directes IP/MPLS sont-elles correctement rattachées à la topologie ? | Config SNMP + mapping |

La corrélation topologique ne vaut que ce que vaut la topologie. Une topologie
incomplète = des cascades mal rattachées = du bruit.

## 4. Audit des briques d'orchestration (pour le dispatch)

| Point à auditer | Question précise | Artefact attendu |
|---|---|---|
| Intégration NBI | i-ENERGY → OUA : déjà intégré (SNMP/API) ou à construire ? | État de l'intégration |
| Feed logistique | La disponibilité GE mobiles / équipes est-elle accessible en temps réel ? | Source de données logistique |
| Canal de crise | Teams + passerelle WhatsApp → ServiceNow en place ? Conforme RGPD (API Meta) ? | Schéma + analyse RGPD |
| ServiceNow | Les workflows d'ouverture/dispatch auto sont-ils configurables côté SN ? | Capacités SN actuelles |

## 5. Livrables de la phase 0

1. **Rapport d'audit** : état réel de chaque brique ci-dessus.
2. **Baseline mesurée** : tes vrais chiffres (à substituer aux `X%` du CCTP).
3. **Registre des manques (gaps)** : ce qui bloque la phase 1, priorisé.
4. **Décision go/no-go phase 1**, par sous-périmètre (corrélation, énergie).

## 6. Méthode et séquencement

- **Semaine 1-2** : extraction des données prestataire sortant (clause réversibilité).
- **Semaine 2-3** : audit i-ENERGY + topologie (avec ZTE si besoin).
- **Semaine 3-4** : audit orchestration + rédaction rapport + go/no-go.

Aligné sur la fenêtre de transition 16 semaines : la phase 0 occupe les 4
premières semaines, avant tout déploiement.

## 7. Les 5 questions qui décident du go/no-go

1. Ma baseline réelle est-elle proche du success story, ou dégradée ?
2. i-ENERGY couvre-t-il tous mes sites nodaux ?
3. L'autonomie i-ENERGY est-elle calibrée et fiable ?
4. Ma topologie OUA (radio + hertzien) est-elle complète ?
5. Le canal de crise et le feed logistique existent-ils déjà ?

Trois "oui" ou plus sur ces cinq points : la phase 1 est lançable. Moins : la
phase 0 doit d'abord combler les manques.
