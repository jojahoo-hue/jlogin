# Commande /transcription

> Analyse une transcription Plaud déposée dans context/import/ et en extrait les éléments clés.

## Ce que tu dois faire

### Étape 1 : Identifier le fichier

Cherche le fichier de transcription le plus récent dans `context/import/` dont le nom contient :
- `plaud`, `transcription`, `reunion`, `formation`, `initiation`, ou tout fichier `.txt` / `.md` récemment ajouté

Si plusieurs fichiers, liste-les et demande lequel traiter.

### Étape 2 : Analyser le contenu

Lis la transcription et extrais :

**Décisions prises**
Liste des décisions claires prises pendant la session.

**Actions à faire**
Todo list concrète avec responsable si mentionné.

**Concepts clés**
Idées, apprentissages, notions importantes à capitaliser dans le Garden Notion.

**Citations importantes**
Phrases marquantes à retenir mot pour mot.

**Contexte**
Type de session (réunion, formation, initiation, conversation), date si disponible, participants si mentionnés.

### Étape 3 : Présenter le résumé structuré

Format de sortie :

---

**Transcription analysée : [nom du fichier]**
**Type :** [réunion / formation / initiation / autre]
**Date :** [si disponible]

**Décisions**
- [décision 1]
- [décision 2]

**Actions**
- [ ] [action 1]
- [ ] [action 2]

**Concepts à capitaliser dans le Garden**
- [concept 1] : [définition ou note]
- [concept 2] : [définition ou note]

**Citations**
> [citation 1]

---

### Étape 4 : Proposer les mises à jour

Selon le contenu analysé, proposer :
- Mise à jour de `context/CONTEXT.md` si nouveau projet ou objectif détecté
- Création d'une note dans `context/import/` avec le résumé structuré
- Entrée dans `context/HISTORY.md`

Attendre confirmation avant d'écrire.

---

## Utilisation typique avec Plaud

1. Enregistrer avec Plaud (réunion, formation, initiation)
2. Exporter la transcription depuis l'app Plaud
3. Renommer le fichier de façon claire : `plaud-AAAA-MM-JJ-[sujet].txt`
4. Déposer dans `context/import/`
5. Taper `/transcription` dans Jarvis

## Règles

- Si la transcription est longue (+5000 mots), résumer par blocs thématiques
- Toujours demander confirmation avant de modifier les fichiers de contexte
- Signaler si le contenu semble privé ou sensible avant de l'archiver
