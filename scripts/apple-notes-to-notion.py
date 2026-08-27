#!/usr/bin/env python3
"""Point d'entrée CLI de la migration Apple Notes -> Notion.

L'implémentation se trouve dans `apple_notes_to_notion.py` (nom importable,
couvert par les tests). Ce fichier ne sert qu'à garder la convention de nommage
des scripts du projet.

Usage : python3 scripts/apple-notes-to-notion.py --dry-run
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from apple_notes_to_notion import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
