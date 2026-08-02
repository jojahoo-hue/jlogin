# Commande /redige

> Ouvre le **Rédacteur Initiatique** (skill `redaction-initiatique`) : écriture d'un livre de transmission
> à partir des conversations, projets, rêves et guidances de Njaho.

---

## Déclenchement

Quand Njaho tape `/redige` (seul) ou `/redige [gabarit + projet + chapitre]`.

- `/redige` seul → activer le skill `redaction-initiatique` et afficher le **menu de démarrage rapide**
  (les 8 gabarits + Numérologie), puis attendre le choix.
- `/redige mémoire vivante projet Ndosi ch.2` (ou toute demande contenant déjà gabarit / projet / chapitre)
  → **sauter le menu** et enchaîner directement la rédaction.

---

## Ce que fait la commande

1. Charge le skill `.claude/skills/redaction-initiatique/SKILL.md`.
2. Applique son démarrage rapide et sa règle d'or UX : **3 infos suffisent (projet · chapitre · gabarit)**,
   une seule question groupée si l'une manque.
3. Déroule le workflow en 6 étapes : cadrage → rédaction (registre ~5000 mots) → règles de style →
   sauvegarde Notion (champ Méthode = gabarit réel) → validation → export `.md`.

---

## Exemples

```
/redige
/redige transmission vivante — tout — le livre entier
/redige ba nitu projet KiTuni chapitre 3
/redige castaneda projet Ndosi ch.1
/redige reprise de manuscrit  (puis joindre le manuscrit en PJ)
/redige numérologie du mot "Kongo"
```

---

## Note

À ne pas confondre avec `/livre` (digestion / lecture rapide d'un livre existant, méthode Readwise).
`/redige` = **écrire** un livre ; `/livre` = **digérer** un livre.
