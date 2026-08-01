# Commande /done

> Bilan de fin de journée. À lancer chaque soir avant de fermer Jarvis.

## Ce que tu dois faire

### Étape 1 : Demander le bilan

Poser ces 3 questions une par une :

```
C'est la fin de ta journée. Trois questions rapides :

1. Qu'est-ce que tu as accompli aujourd'hui ? (liste libre, même les petites choses)
```

Attendre la réponse, puis :

```
2. Qu'est-ce qui était prévu et n'a pas été fait ? (sans jugement, juste pour tracer)
```

Attendre la réponse, puis :

```
3. Une chose que tu retiens de cette journée — une idée, une décision, un apprentissage ?
```

### Étape 2 : Synthèse

Présenter un résumé court :

```
Bilan du [date].

Accompli : [liste]
Reporté : [liste]
Retenu : [élément clé]

Score d'énergie subjectif : [demander si 1-10 si utile]
```

### Étape 3 : Mise à jour automatique

Sans attendre confirmation, ajouter une entrée compacte dans `context/HISTORY.md` :

```
## [AAAA-MM-JJ] — Bilan journée
- Accompli : [synthèse en 1 ligne]
- Reporté : [synthèse en 1 ligne]
- Retenu : [idée clé]
```

### Étape 4 : Clôture

Terminer par :

```
Bonne soirée Njaho. À demain avec /morning.
```

---

## Règles

- Maximum 5 minutes d'interaction
- Pas de jugement, pas de coaching forcé
- Si Njaho répond "rien" ou "tout" sans détail, accepter et archiver tel quel
- Le bilan sert uniquement à créer une mémoire continue, pas à évaluer la performance
