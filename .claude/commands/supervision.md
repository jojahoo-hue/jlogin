# Commande /supervision

> Assistant IA pour le centre de supervision réseau de Njaho.
> Triage d'incidents, troubleshooting assisté, rapports, automatisation.

---

## Modes disponibles

Quand Njaho tape `/supervision`, demander quel mode activer :

```
Centre de supervision — que veux-tu faire ?

1. /supervision incident   → Ouvrir et traiter un incident en cours
2. /supervision bilan      → Bilan des incidents de la journée / semaine
3. /supervision process    → Documenter ou générer un process d'intervention
4. /supervision auto       → Identifier ce qui peut être automatisé
5. /supervision formation  → Générer un support de formation technique
```

---

## Mode 1 : /supervision incident

### Étape 1 — Qualification rapide

Poser ces questions une par une :

```
Incident en cours. Qualification rapide.

1. Quel équipement ou service est impacté ?
   (Ex : "routeur BRAS-01", "fibre optique zone nord", "service VoIP")
```

```
2. Quelle est la nature du défaut ?
   (Ex : "perte de lien", "saturation de bande passante", "alarme critique", "plaintes clients")
```

```
3. Périmètre impacté : combien de clients / sites / équipements touchés ?
```

```
4. Depuis quand ? Heure de début de l'incident.
```

```
5. Déjà un ticket ServiceNow ouvert ? Si oui, donne-moi le numéro.
```

### Étape 2 — Analyse et triage IA

Sur la base des réponses, générer :

**Niveau de priorité**
- P1 : Impact client massif, service critique down
- P2 : Impact client partiel ou service dégradé
- P3 : Impact limité ou préventif

**Hypothèses de cause probable**
Liste des causes les plus probables par ordre de probabilité, basée sur le type d'équipement et la nature du défaut.

**Plan de troubleshooting**
Étapes ordonnées à suivre pour diagnostiquer et résoudre.

**Actions immédiates**
Ce qu'il faut faire dans les 15 prochaines minutes.

**Escalade recommandée**
Si escalade nécessaire : à qui, avec quel niveau d'urgence.

### Étape 3 — Suivi

À la résolution, demander :
```
Incident résolu ?
- Cause racine identifiée ?
- Solution appliquée ?
- Action préventive à documenter ?
```

Générer un **compte-rendu d'incident** formaté pour ServiceNow.

---

## Mode 2 : /supervision bilan

Demander la période (aujourd'hui / cette semaine / ce mois).

Générer un tableau de bord textuel :

```
BILAN SUPERVISION — [Période]

Incidents traités : [nombre]
  P1 : [nombre] — MTTR moyen : [durée]
  P2 : [nombre] — MTTR moyen : [durée]
  P3 : [nombre] — MTTR moyen : [durée]

Cause racine principale : [type le plus fréquent]
Zone la plus impactée : [zone géographique ou équipement]

Incidents récurrents détectés :
- [Incident type 1 : X occurrences → action préventive suggérée]
- [Incident type 2 : X occurrences → action préventive suggérée]

Actions préventives recommandées :
1. [Action 1]
2. [Action 2]
```

Proposer d'enregistrer le bilan dans `context/import/supervision-bilan-[date].md`.

---

## Mode 3 : /supervision process

Demander :
```
Quel process veux-tu documenter ou générer ?
(Ex : "process alarme BRAS", "process intervention fibre", "process escalade P1")
```

Générer un document structuré :
- Déclencheur
- Acteurs impliqués
- Étapes ordonnées avec points de décision
- Critères de résolution
- Format compatible pour transfert vers ServiceNow ou SharePoint

---

## Mode 4 : /supervision auto

Analyser les incidents décrits en session et identifier :

```
OPPORTUNITÉS D'AUTOMATISATION DÉTECTÉES

Tâches répétitives identifiées :
- [Tâche 1] : fréquence estimée [X/semaine] → automatisation possible via [outil/script]
- [Tâche 2] : fréquence estimée [X/semaine] → automatisation possible via [outil/script]

Priorité d'automatisation recommandée :
1. [Tâche la plus impactante] — gain estimé : [X heures/semaine]
   Approche : [script Python / ServiceNow workflow / agent IA]

2. [Tâche suivante]
   Approche : [...]

Proof-of-concept suggéré pour cette semaine :
[Une seule automatisation concrète à implémenter en premier]
```

---

## Mode 5 : /supervision formation

Demander :
```
Sur quel sujet technique veux-tu créer un support de formation ?
(Ex : "troubleshooting MPLS", "lecture alarmes SNMP", "procédure de changement")

Pour quel public ? (techniciens terrain, NOC niveau 1, ingénieurs)
```

Générer un support structuré :
- Objectifs pédagogiques
- Contenu technique par niveau
- Cas pratiques basés sur des incidents réels
- QCM de validation
- Format exportable vers Gamma ou PowerPoint

---

## Règles générales

- Toujours qualifier la priorité avant d'entrer dans le détail
- Ne jamais inventer des données réseau : travailler uniquement avec ce que Njaho fournit
- Les comptes-rendus d'incidents sont enregistrés dans `context/import/` si Njaho le demande
- Pour les processus récurrents, suggérer une fiche process dédiée dans Notion (section Process de l'architecture IPSRA)
- Adapter le niveau technique selon le contexte : opérationnel pour le terrain, stratégique pour les bilans
