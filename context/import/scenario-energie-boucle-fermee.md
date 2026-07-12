# Fiche technique — Boucle fermée énergie (site nodal sur batterie)

> Scénario d'auto-remédiation orchestrée pour les incidents énergie sur sites
> nodaux. Premier périmètre de boucle fermée du programme d'automatisation NOC.
> Source de télémétrie : EMS **i-ENERGY ZTE**. Moteur : OCUA + ServiceNow.
>
> Généré le 2026-07-12. Document de travail interne.

---

## 1. Principe de sécurité

**Aucune action sur les équipements réseau.** L'automatisation est purement de
l'orchestration : corrélation, ticketing, dispatch, notification. La décision
automatisée est "envoyer un groupe électrogène", jamais "agir sur un
équipement réseau". C'est ce qui rend la boucle fermée défendable sans risque
de panne provoquée.

## 2. Source de télémétrie : i-ENERGY ZTE

Données remontées par site, à intégrer dans OCUA :

| Donnée | Usage dans la boucle |
|---|---|
| État secteur (mains status) | Détection racine, anti-flapping |
| Redresseur en décharge | Confirmation bascule batterie |
| Tension DC (48V → seuils) | Suivi de dégradation |
| SOC (état de charge %) | Calcul de priorité |
| **Temps d'autonomie restant estimé** | **Variable de déclenchement du dispatch** |
| Température / défaut climatisation | Scénario parallèle surchauffe |

**Intégration à spécifier :** remontée i-ENERGY ZTE → OCUA via interface
Northbound (SNMP traps pour les alarmes, API REST / fichiers pour les KPIs
énergie). Point à valider avec le prestataire et ZTE.

## 3. Arbre de corrélation

```
[RACINE]  AC input fail / Mains failure (i-ENERGY ZTE)
   │
   ├─[ÉNERGIE]  Rectifier on battery discharge
   │            Low battery voltage (seuils DC)
   │            Remaining backup time décroissant
   │
   ├─[CLIMATISATION]  High temperature / AC fail (branche parallèle)
   │
   └─[CONSÉQUENTES RÉSEAU]  (supprimées, rattachées à la racine)
        Perte cellules du site nodal (EMS RAN Nokia MantaRay)
        Perte des liens hertziens portant les sites subordonnés (NetNumen ZTE)
        Perte des sites subordonnés (topologie)
        Indisponibilité RAN/transport agrégée zone (proxy impact, core hors périmètre)
```

- **Causale** : l'alarme énergie racine domine, les alarmes réseau sont ses
  conséquences → suppression conditionnelle et rattachement à l'incident parent.
- **Topologique** : OCUA identifie les sites subordonnés au nodal.
- **Temporelle** : fenêtre d'agrégation de la cascade.

Sortie : un incident unique, ex. *"Site nodal X sur batterie, autonomie estimée
45 min (SOC 62%), 6 sites subordonnés impactés via hertzien, indisponibilité
RAN/transport agrégée zone Y"*.

## 4. Logique de déclenchement (conditionnelle)

```
SI   mains_status = FAIL depuis > T_anti_flap        # ex. 5 min
ET   remaining_backup_time < SEUIL_AUTONOMIE          # ex. 60 min
ET   site.criticite >= SEUIL_CRITICITE                # nodal ou N sites portés
ALORS
     -> ouvrir/enrichir ticket ServiceNow (priorité = f(autonomie, criticité))
     -> supprimer et rattacher les alarmes subordonnées
     -> dispatch logistique : demande GE mobile + fiche accès site
     -> notification QHSE (intervention physique)
     -> alerte astreinte/manager via canal de crise (Teams + WhatsApp)
FIN

AU RETOUR  mains_status = OK  OU  GE en ligne :
     -> auto-clear incident et tickets liés
```

**Calcul de priorité du ticket** = combinaison de :
- temps d'autonomie restant (plus court = plus prioritaire),
- criticité du site (nombre de sites subordonnés, service impacté),
- contexte (nuit, météo, nombre d'événements concurrents).

## 5. Garde-fous

| Garde-fou | Rôle |
|---|---|
| Anti-flapping (T_anti_flap) | Une coupure brève ne déclenche pas de dispatch |
| Seuil d'autonomie | Pas de dispatch tant que la batterie tient largement |
| Limite de fréquence | Pas plus de N déclenchements auto / site / fenêtre |
| Fenêtre de veto humain (recommandé) | Dispatch GE auto-proposé, 5 min de veto opérateur avant envoi ferme |
| Kill switch | Suspension manuelle de la boucle à tout instant |
| Journalisation ServiceNow | Chaque action auto tracée (règle, horodatage, résultat) |
| Validation staging | Aucune mise en prod sans test de basculement validé |

**Arbitrage à trancher (Njaho) :** boucle pleinement fermée (dispatch auto ferme)
vs semi-fermée (veto humain de 5 min). Recommandation : semi-fermée en phase 1
sur l'action GE, car c'est l'action la plus coûteuse et la moins réversible.

## 6. Points à valider avant mise en oeuvre

1. **Couverture i-ENERGY ZTE** : tous les sites nodaux sont-ils équipés et
   remontés ? Les sites à alimentation non-ZTE sont-ils couverts autrement ?
2. **Fiabilité du "remaining backup time"** : l'estimation d'autonomie est-elle
   calibrée (âge batteries, charge réelle) ou théorique ? Une estimation fausse
   fausse le seuil de déclenchement.
3. **Feed logistique** : la disponibilité des GE mobiles et des équipes est-elle
   accessible en temps réel pour l'arbitrage multi-sites ?
4. **Passerelle canal de crise** : la synchro Teams + WhatsApp → ServiceNow est
   -elle en place et conforme RGPD (API Meta) ?
5. **Intégration NBI i-ENERGY → OCUA** : SNMP + API à cadrer avec ZTE.

## 7. Phasage proposé

- **Phase 0** : audit couverture i-ENERGY + calibration autonomie + intégration NBI.
- **Phase 1** : corrélation racine énergie + suppression alarmes subordonnées +
  ticket auto enrichi. Pas encore de dispatch auto. Mesure.
- **Phase 2** : notification/dispatch semi-fermé (veto humain) sur sites nodaux.
- **Phase 3** : boucle pleinement fermée sur sous-ensemble validé, si les
  résultats de phase 2 le justifient.

---

### Note (à retirer avant diffusion)

Ce scénario devient un argument fort de ton RFP : tu exiges du prestataire qu'il
exploite la télémétrie i-ENERGY ZTE existante pour l'orchestration énergie, avec
la baseline et les garde-fous ci-dessus. Tu ne demandes pas une techno nouvelle,
tu demandes de tirer parti de ce que tu as déjà.
