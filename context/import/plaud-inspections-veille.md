# Plaud / Notion — Inspections & résumés de la veille

> Source : MCP Notion (base **🎙️ Plaud Archive** + espace de travail « Notion de Johan Login »).
> Récupéré le 2026-07-31 pour alimenter le contexte Jarvis.
> Fichier additif, généré automatiquement. Ne remplace pas `CONTEXT.md`.

---

## Note d'interprétation (à valider)

- « Le MCP Plaud » = il n'existe pas de MCP Plaud autonome. Plaud exporte les enregistrements vers **Notion**, et c'est le **MCP Notion** qui sert de passerelle. L'ID réel de la base Plaud a été renseigné dans `notion-config.json` (il était encore en placeholder).
- « Les quatre inspections » = le lot QHSE / **Visite d'Inspection Commune (VIC)** ci-dessous. Deux comptes rendus substantiels ont été extraits en entier, deux analyses associées sont indexées. **Si tu visais quatre autres inspections précises, dis-le, je réajuste.**
- « Les résumés de la veille » = les pages produites le **2026-07-30**.

---

## 1. Les quatre inspections (QHSE / VIC)

### 1.1 Compte rendu — Visite d'Inspection Commune, Site Télécom (Orange)
Source : https://app.notion.com/p/3ae92f894f8c816c9148e126c59e3570 — réunion du 2026-02-23.

**Synthèse.** Site propriété Orange, espace loué aux intervenants (Axence, KAINA), périmètre d'accès à clarifier entre zone technique et pylône. Accès mal verrouillé et pratique opérationnelle non conforme : interventions énergie/hauteur trop souvent en personne isolée, sans PTI ni moyens de secours, alors que le Code du travail impose un binôme habilité de même niveau et une préparation des secours. Décisions actées : sécurisation par cadenas/clé (plutôt que badges) et bascule vers des interventions à deux. Restent non formalisés : gouvernance documentaire (Plan de Prévention / PPA), cartographie des accès, dispositif « homme mort ».

**Actions à mener (@Njaho / exploitation)**
- [ ] Installer des cadenas et formaliser la segmentation des accès (zone technique, passage câbles, pylône) avec procédure de clé en boîte à clés.
- [ ] Rédiger et valider le PPA/Plan de Prévention du site : périmètres d'accès, consignation/enclencheur général, binôme obligatoire (énergie/hauteur), habilitations, moyens de secours, protocole PTI.
- [ ] Mettre la clé pylône en boîte à clés et diffuser la procédure d'accès aux équipes habilitées.
- [ ] Basculer les interventions énergie/hauteur en binôme certifié (même niveau d'habilitation) et mettre à jour les modes opératoires.
- [ ] Réaliser le jeu de photos de la zone technique et du parcours d'accès pour le PPA et le brief des équipes.
- [ ] Valider avec Orange le schéma de propriété et les responsabilités d'accès/sécurisation (équipements vs dalle), consigner l'accord dans le PPA.

**Points de sécurité travail en hauteur (Risel/Rysol)** : Orange interdit tout décrochement du risel (accidents) ; double accrochage requis à la première ascension ; ne pas monter avec équipements attachés au harnais ; annexer les MODOP au plan de prévention ; vérification visuelle du pylône avant intervention.

### 1.2 Compte rendu — Réunion sécurité / préparation VIC
Source : https://app.notion.com/p/3ae92f894f8c8193b8adce18d7963f44 — réunion du 2026-02-25 (participants : Johan Login, Yoann Seguin Cadiche, Patrice Francillette).

**Synthèse.** Méthode de conduite des VIC retenue avec le prestataire QHSE (Yoann Seguin Cadiche) : demander aux entreprises leur **mode opératoire + analyse de risque** avant la visite (pas de trame imposée, adaptation à leurs documents), préparer les problématiques en amont, puis réaliser la visite, produire le compte rendu de visite, mettre à jour le plan de prévention et faire ajuster les MODOP si besoin. Cas Saint-Martin : un prestataire sans habilitation électrique peut réaliser le plan de prévention en attendant (formation en cours de négociation). Dates d'intervention discutées (autour des 7/8/9).

### 1.3 Analyse juridique — Inspection commune préalable (ICP / VIC)
Source : https://app.notion.com/p/3ae92f894f8c8110bf8cd1dc05efc2b3 (indexée).
Cadre légal de l'obligation d'inspection commune préalable entre entreprise utilisatrice et entreprises extérieures.

### 1.4 Vérification du plan de prévention
Source : https://app.notion.com/p/3ae92f894f8c8102985ce34c34cea9d4 (indexée).
Article R4512-6 du Code du travail : obligation d'inspection commune préalable. Point de contrôle de conformité des plans de prévention.

**Autres pièces du même lot QHSE (30-31/07, pour mémoire)** : Déroulé entretien QHSE, Avancement politique QHSE, Consultant QHSE MADIACOM, Gouvernance QHSE TowerCo PTI, REX sécurisation alimentation 48V, Réconciliation Plans de Prévention.

---

## 2. Résumés de la veille (2026-07-30)

- **Refonte Architecture IT MediaCom** — https://app.notion.com/p/3ad92f894f8c81d78b5bcb6c8573a492
  Panorama sécurité réseau : pare-feu nouvelle génération, IPS/IDS, filtrage URL, inspection applicative.
- **Analyse défaillances organisationnelles** — https://app.notion.com/p/3ad92f894f8c810398fdcd1936c269b5
  Exploitation des stats site sur Ienergy (période 2 mois, granularité jour) pour caractériser des défaillances.
- **Transcription carrousel Instagram** — https://app.notion.com/p/3ad92f894f8c81ada876d64f2cddd7d4
  Transcription d'un carrousel Instagram (contenu artistique / communication).

---

## Suite possible

- Extraire en entier les pièces 1.3, 1.4 et les résumés du 30/07 (actuellement indexés) sur demande.
- Une fois validé, reporter les points structurants (PPA, binôme obligatoire, sécurisation des accès) dans `CONTEXT.md` › projet « Digitalisation / sécurisation exploitation ».
