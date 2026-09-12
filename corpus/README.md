# Corpus

Matière première locale pour la rédaction des livres. Produite depuis Notion
`🎙️ Plaud Archive`, elle-même alimentée par Plaud.

## Contenu

| Chemin | Suivi par git | Rôle |
|---|---|---|
| `taxonomie.yaml` | oui | taxonomie contrôlée, 40 thèmes, source de vérité |
| `INDEX.md` | oui | inventaire lisible, groupé par livre et par thème |
| `index.json` | oui | inventaire machine, consommé par les scripts |
| `plaud-listing.json` | oui | inventaire brut côté Plaud, produit par `/corpus listing` |
| `plaud-manquants.json` | oui | écart Plaud vers Notion |
| `fiches/*.md` | **non par défaut** | transcriptions intégrales |

## Pourquoi les fiches ne sont pas versionnées par défaut

Elles contiennent 620 heures de sessions initiatiques, de consultations et de
conversations privées, plus des réunions professionnelles couvertes par le secret
des affaires. Les pousser sur un dépôt GitHub distant est une décision qui
appartient à Njaho, pas au script.

Trois options, à choisir explicitement :

1. **Rester en local** (défaut actuel). `corpus/fiches/` est dans `.gitignore`.
   Les fichiers vivent sur le Mac, sauvegardés par Time Machine. Claude Code y
   accède en local, le grep fonctionne. Aucun risque de diffusion.
2. **Dépôt privé dédié**. Un second dépôt git privé, distinct de `jlogin`,
   uniquement pour le corpus. Versionné, sauvegardé, mais séparé du reste.
3. **Tout versionner ici**. Retirer la ligne de `.gitignore`. À ne faire que si
   le dépôt `jlogin` est et reste privé, et qu'aucun collaborateur n'y a accès.

## Structure d'une fiche

```
---
plaud_id: 922ec327fc64b934e43b900a2663feed
notion_url: https://app.notion.com/...
titre: "09-12 Séance: Méditation, Énergie et Astrologie"
date: 2026-09-12
duree_min: 186
dossier: "Spiritualité & Développement personnel"
statut_plaud: Transcrit
themes: ["Méditation guidée", "Astrologie"]
livre_cible: "Mpévé Ya Bakala"
mots_cles: "méditation, nettoyage énergétique, ..."
transcription: oui
derniere_maj: 2026-09-12
---

# Titre

## Résumé
## Actions
## Sujets bruts (Plaud)
## Transcription intégrale
```

L'en-tête YAML est fait pour le grep, pas pour la lecture. C'est lui qui permet
de sélectionner les sources d'un chapitre sans ouvrir un seul fichier en entier.

## Ordre des opérations

```bash
python3 scripts/corpus_export.py        # 1. sauvegarde locale, toujours en premier
python3 scripts/notion_taxonomie.py     # 2. rapport taxonomie
python3 scripts/notion_taxonomie.py --apply
python3 scripts/manuscrits_dedup.py     # 3. rapport doublons
python3 scripts/manuscrits_dedup.py --apply
# 4. dans Claude Code : /corpus listing puis /corpus rattrapage
# 5. dans Claude Code : /manuscrit <livre> plan
```

Aucun script destructif ne tourne tant que `corpus/index.json` n'existe pas.
C'est volontaire.
