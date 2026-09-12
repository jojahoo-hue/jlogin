# Livres

Un dossier par livre, créé par `scripts/manuscrits_dedup.py` lors de la première
sauvegarde, puis alimenté par `/manuscrit <livre> chapitre <N>`.

```
livres/<slug-du-livre>/
├── PLAN.md            table des chapitres, angles, sources
├── GLOSSAIRE.md       vocabulaire kikongo, chapitre de première occurrence
├── chapitres/         un .md par chapitre (non versionné par défaut)
└── <slug>-complet.md  manuscrit assemblé
```

Les chapitres ne sont pas versionnés par défaut, pour la même raison que le corpus.
Voir `corpus/README.md`.

## Les neuf titres

| Livre | Thèmes sources |
|---|---|
| Thot Mfumu TuTi dia Tiya | Géométrie sacrée, Numérologie et arithmosophie |
| Nza Nga dia KiTuni | Kalunga et univers de la mort, Lignées, Ancêtres |
| Nza Ngai dia Ndosi | Retraites RIK et RSK, Rêve et décorporation |
| Nza Ngai dia Nzayi | Cosmologie Kongo, Muntu, Éthique communautaire |
| Tablette de Thot | Kemet, Égypte et Nubie |
| Nza Nga dia Mbazi | Protection énergétique, Longo, Couple et sexualité sacrée |
| Nza ngai Sono Zi Tiya | Sceaux et cartouches, Sono-zi-tiya |
| Leadership Totémique | Totems, Leadership totémique, Abondance |
| Mpévé Ya Bakala | Méditation guidée |

La correspondance thème vers livre est portée par `corpus/taxonomie.yaml`.
