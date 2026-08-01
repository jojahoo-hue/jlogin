# Commande /prime

> Charge le contexte complet de Njaho au début de chaque session.

## Ce que tu dois faire

1. Lis les 3 fichiers dans cet ordre :
   - `CLAUDE.md` (instructions et profil de base)
   - `context/CONTEXT.md` (contexte détaillé : activité, objectifs, projets)
   - `context/HISTORY.md` (journal des sessions passées et dernières décisions)

2. Vérifie aussi si des documents sont présents dans `context/import/` et signale-les si c'est le cas.

3. Présente un résumé structuré de ce que tu sais, sous cette forme :

---

**Jarvis prêt.**

Bonjour Njaho. Voici ce que je sais de toi au démarrage de cette session :

**Qui tu es**
[Synthèse en 2 lignes du profil]

**Tes projets actifs**
[Liste des projets en cours tirés de CONTEXT.md]

**Dernière session**
[Dernière entrée de HISTORY.md, date et résumé]

**Documents en attente d'analyse**
[Si des fichiers sont dans context/import/, les lister. Sinon : "Aucun document en attente."]

Qu'est-ce qu'on fait aujourd'hui ?

---

## Règles

- Sois direct, pas de blabla
- Si HISTORY.md est vide ou ne contient que l'entrée d'installation, dis simplement "Première session depuis l'installation."
- Si un fichier est manquant ou vide, signale-le sans paniquer
