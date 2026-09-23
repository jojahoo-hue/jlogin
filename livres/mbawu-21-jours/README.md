# Mbawu, les vingt et un jours

> Livre **Nza Ngai dia Nzayi**, méthode Transmission Vivante.
> Le manuscrit vit dans Notion, base **Manuscrits — Chapitres Rédigés**.
> Ce dossier sert au pilotage, pas au stockage du texte.

---

## État réel du manuscrit

Relevé le 2026-09-23 depuis Notion.

| Élément | Chapitres | Mots | État |
|---------|-----------|------|------|
| Préface, Introduction, Seuil | 3 | 7 673 | Rédigés |
| Jours 1 à 17 (chapitres 1 à 18) | 18 | 65 945 | Rédigés |
| **Jours 18 et 19 (chapitres 19 et 20)** | **2** | **0** | **Manquants, sources absentes** |
| Jour 20 (chapitre 21) | 1 | 3 931 | **Rédigé le 2026-09-23** |
| Jour 21 (chapitre 22) | 1 | 4 549 | **Rédigé le 2026-09-23** |

Total actuel : **24 textes, environ 82 000 mots** pour la partie Transmission Vivante.

Le même livre porte aussi 11 chapitres de méthode **Castaneda** rédigés le 2026-06-17
(préface, introduction, 8 chapitres, conclusion, environ 44 400 mots). Deux manuscrits
distincts cohabitent sous le même titre dans la base. Arbitrage éditorial à faire :
deux volumes, ou un seul.

---

## Correspondance jour / chapitre

Le chapitre N raconte le jour N-1 à partir du chapitre 15 environ. Le décalage vient du
quatorzième jour, qui a produit deux conversations sources et occupe deux chapitres.

Repères vérifiés :

- Chapitre 2 — jour 2, mardi 23 juin 2026
- Chapitre 18 — **jour 17**, mercredi 8 juillet 2026, feu vert et blanc
- Chapitre 21 — jour 20, samedi 11 juillet 2026, flamme verte et dorée
- Chapitre 22 — jour 21, dimanche 12 juillet 2026, Bouclier des Douze Flammes

---

## Ce qui manque

**Les jours 18 et 19, soit jeudi 9 et vendredi 10 juillet 2026.**

Aucune conversation correspondante dans la base Notion `ChatGPT conversations`, qui
contient pourtant les vingt autres journées. Ces deux jours tombent entre le retour des
urgences et le début de la retraite à Pointe-Noire.

Pistes à explorer, par ordre de probabilité :

1. Enregistrements Plaud non exportés vers Notion pour ces deux dates
2. Conversation ChatGPT non archivée par le connecteur, à retrouver dans l'historique
3. Journal papier ou notes du téléphone
4. Dictée neuve : les sept lignes du Journal de Mbawu pour ces deux jours, de mémoire

Sans source, ces deux chapitres ne seront pas écrits. Le livre peut se clore sans eux, à
condition de l'assumer dans le texte plutôt que de laisser un trou silencieux entre les
chapitres 18 et 21.

---

## Reste à faire

- [ ] Retrouver ou redicter les jours 18 et 19, ou décider de les traiter comme une ellipse assumée
- [ ] Trancher : un volume ou deux, entre Transmission Vivante et Castaneda
- [ ] Écrire la conclusion du cycle, après le chapitre 22
- [ ] Renuméroter la Préface, l'Introduction et le Seuil, dont le champ `Numéro` est vide ou à 0
- [ ] Relecture fidélité, cohérence, langue, voir les trois passes de `/ecrire-livre`
- [ ] Décider du traitement des prénoms réels, voir `PLAN.md` section 2
- [ ] Assembler et exporter, ePub ou Word

---

## Où est quoi

```
Notion  Manuscrits — Chapitres Rédigés   le manuscrit, source de vérité
Notion  ChatGPT conversations            les journaux sources, filtre rik = Nza Ngai dia Nzayi
local   livres/mbawu-21-jours/PLAN.md    cadrage éditorial et périmètre de non-divulgation
local   livres/mbawu-21-jours/chapitres/ copie de travail, exclue de Git
```

Le dépôt `jojahoo-hue/jlogin` est **public**. Ni les chapitres ni les notes sources n'y
sont versionnés, le `.gitignore` les bloque. Voir `PLAN.md` section 2.
