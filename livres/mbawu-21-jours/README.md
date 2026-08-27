# Mbawu, les vingt-et-un jours

> Projet de livre issu du projet **Nza Ngai dia Nzayi**.
> Piloté par la commande `/ecrire-livre`.

---

## État du chantier

| Phase | Statut | Détail |
|-------|--------|--------|
| 0. Collecte des sources | **Bloquée** | Notes dans Notion, non accessibles depuis le cloud Claude Code |
| 1. Cadrage éditorial | En attente | 5 questions à trancher, voir `PLAN.md` |
| 2. Architecture | Ébauche | Squelette proposé dans `PLAN.md`, à valider |
| 3. Rédaction | Non démarrée | |
| 4. Relecture | Non démarrée | |
| 5. Export | Non démarrée | |

Dernière mise à jour : 2026-08-27

---

## Ce qui bloque

Les notes du projet Nza Ngai dia Nzayi vivent dans Notion. Cette session Claude Code
tourne dans le cloud, où `api.notion.com` est filtré et où aucun `NOTION_TOKEN` n'est
présent. Impossible de lire la matière d'ici.

Aucune ligne du livre ne sera écrite avant que les notes soient dans
`livres/mbawu-21-jours/notes-sources/`. Écrire sur les vingt-et-un jours sans la matière
reviendrait à inventer une tradition, ce qui est exactement l'inverse du but.

## Comment débloquer

Trois voies, de la plus propre à la plus rapide. Le détail est dans
`notes-sources/README.md`.

- **A. Sync Notion depuis le Mac** : renseigner l'ID de la page projet dans
  `notion-config.json`, lancer `python3 scripts/sync-notion.py`, pousser
- **B. Export Notion manuel** : Markdown & CSV, dézippé dans `notes-sources/`
- **C. Copier-coller** : coller les notes dans la conversation, Claude les classe

---

## Arborescence

```
livres/mbawu-21-jours/
├── README.md          # ce fichier, pilotage
├── PLAN.md            # cadrage et architecture éditoriale
├── glossaire.md       # vocabulaire initiatique, alimenté au fil de l'écriture
├── notes-sources/     # matière brute exportée de Notion
└── chapitres/         # un fichier par chapitre, créés après validation du PLAN
```
