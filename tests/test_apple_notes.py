"""Tests de la migration Apple Notes -> Notion (partie conversion, sans réseau)."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

from apple_notes_to_notion import (  # noqa: E402
    MAX_TEXT_LENGTH,
    build_properties,
    markdown_to_blocks,
    parse_front_matter,
    parse_inline,
    read_notes,
    split_title_and_body,
)


def plain(rich_text):
    return "".join(rt["text"]["content"] for rt in rich_text)


class TestParseInline(unittest.TestCase):
    def test_texte_simple(self):
        rt = parse_inline("Bonjour Njaho")
        self.assertEqual(len(rt), 1)
        self.assertEqual(rt[0]["text"]["content"], "Bonjour Njaho")
        self.assertNotIn("annotations", rt[0])

    def test_gras_et_italique(self):
        rt = parse_inline("un **mot** et _autre_")
        self.assertEqual(plain(rt), "un mot et autre")
        self.assertTrue(rt[1]["annotations"]["bold"])
        self.assertTrue(rt[3]["annotations"]["italic"])

    def test_code_inline(self):
        rt = parse_inline("lance `pytest` maintenant")
        self.assertTrue(rt[1]["annotations"]["code"])
        self.assertEqual(rt[1]["text"]["content"], "pytest")

    def test_barre(self):
        rt = parse_inline("~~annulé~~")
        self.assertTrue(rt[0]["annotations"]["strikethrough"])

    def test_lien_markdown(self):
        rt = parse_inline("voir [le site](https://exemple.fr) ici")
        self.assertEqual(rt[1]["text"]["link"]["url"], "https://exemple.fr")
        self.assertEqual(rt[1]["text"]["content"], "le site")

    def test_url_nue(self):
        rt = parse_inline("source https://exemple.fr fin")
        self.assertEqual(rt[1]["text"]["link"]["url"], "https://exemple.fr")

    def test_annotations_imbriquees(self):
        rt = parse_inline("**gras et _italique_**")
        italique = [r for r in rt if r.get("annotations", {}).get("italic")]
        self.assertTrue(italique)
        self.assertTrue(italique[0]["annotations"]["bold"])

    def test_decoupage_texte_trop_long(self):
        rt = parse_inline("a" * (MAX_TEXT_LENGTH + 50))
        self.assertEqual(len(rt), 2)
        self.assertEqual(len(rt[0]["text"]["content"]), MAX_TEXT_LENGTH)

    def test_underscore_dans_un_mot_non_italique(self):
        rt = parse_inline("nom_de_variable")
        self.assertEqual(len(rt), 1)
        self.assertNotIn("annotations", rt[0])


class TestMarkdownToBlocks(unittest.TestCase):
    def test_titres(self):
        blocks, _ = markdown_to_blocks("# Un\n## Deux\n#### Quatre")
        self.assertEqual([b["type"] for b in blocks],
                         ["heading_1", "heading_2", "heading_3"])

    def test_listes(self):
        blocks, _ = markdown_to_blocks("- a\n* b\n• c\n1. d\n2) e")
        self.assertEqual([b["type"] for b in blocks],
                         ["bulleted_list_item"] * 3 + ["numbered_list_item"] * 2)

    def test_cases_a_cocher_markdown(self):
        blocks, _ = markdown_to_blocks("- [ ] à faire\n- [x] fait")
        self.assertEqual(blocks[0]["type"], "to_do")
        self.assertFalse(blocks[0]["to_do"]["checked"])
        self.assertTrue(blocks[1]["to_do"]["checked"])

    def test_cases_a_cocher_apple(self):
        blocks, _ = markdown_to_blocks("☐ acheter du pain\n☑ appeler Paul")
        self.assertEqual(blocks[0]["type"], "to_do")
        self.assertFalse(blocks[0]["to_do"]["checked"])
        self.assertTrue(blocks[1]["to_do"]["checked"])
        self.assertEqual(plain(blocks[1]["to_do"]["rich_text"]), "appeler Paul")

    def test_citation_multiligne(self):
        blocks, _ = markdown_to_blocks("> ligne un\n> ligne deux\n\ntexte")
        self.assertEqual(blocks[0]["type"], "quote")
        self.assertEqual(plain(blocks[0]["quote"]["rich_text"]), "ligne un\nligne deux")
        self.assertEqual(blocks[1]["type"], "paragraph")

    def test_separateur(self):
        blocks, _ = markdown_to_blocks("a\n\n---\n\nb")
        self.assertEqual([b["type"] for b in blocks], ["paragraph", "divider", "paragraph"])

    def test_bloc_de_code(self):
        blocks, _ = markdown_to_blocks("```py\nprint(1)\nprint(2)\n```")
        self.assertEqual(blocks[0]["type"], "code")
        self.assertEqual(blocks[0]["code"]["language"], "python")
        self.assertEqual(plain(blocks[0]["code"]["rich_text"]), "print(1)\nprint(2)")

    def test_langage_inconnu_devient_plain_text(self):
        blocks, _ = markdown_to_blocks("```klingon\nabc\n```")
        self.assertEqual(blocks[0]["code"]["language"], "plain text")

    def test_tableau(self):
        md = "| Nom | Rôle |\n| --- | --- |\n| Njaho | Auteur |"
        blocks, _ = markdown_to_blocks(md)
        table = blocks[0]
        self.assertEqual(table["type"], "table")
        self.assertEqual(table["table"]["table_width"], 2)
        self.assertTrue(table["table"]["has_column_header"])
        self.assertEqual(len(table["table"]["children"]), 2)
        self.assertEqual(plain(table["table"]["children"][1]["table_row"]["cells"][0]), "Njaho")

    def test_image_distante(self):
        blocks, attachments = markdown_to_blocks("![](https://exemple.fr/a.png)")
        self.assertEqual(blocks[0]["type"], "image")
        self.assertEqual(attachments, [])

    def test_piece_jointe_locale_signalee(self):
        blocks, attachments = markdown_to_blocks("![](images/photo.png)")
        self.assertEqual(blocks[0]["type"], "callout")
        self.assertEqual(attachments, ["images/photo.png"])

    def test_paragraphe_regroupe_les_lignes(self):
        blocks, _ = markdown_to_blocks("ligne un\nligne deux\n\nautre")
        self.assertEqual(len(blocks), 2)
        self.assertEqual(plain(blocks[0]["paragraph"]["rich_text"]), "ligne un\nligne deux")

    def test_paragraphe_stoppe_sur_un_nouveau_bloc(self):
        blocks, _ = markdown_to_blocks("texte\n- puce")
        self.assertEqual([b["type"] for b in blocks], ["paragraph", "bulleted_list_item"])

    def test_document_vide(self):
        blocks, attachments = markdown_to_blocks("")
        self.assertEqual(blocks, [])
        self.assertEqual(attachments, [])

    def test_fins_de_ligne_windows(self):
        blocks, _ = markdown_to_blocks("# Titre\r\n\r\n- a\r\n")
        self.assertEqual([b["type"] for b in blocks], ["heading_1", "bulleted_list_item"])
        self.assertEqual(plain(blocks[0]["heading_1"]["rich_text"]), "Titre")


class TestListesImbriquees(unittest.TestCase):
    def test_deux_niveaux(self):
        blocks, _ = markdown_to_blocks("- parent\n    - enfant\n- autre parent")
        self.assertEqual(len(blocks), 2)
        enfants = blocks[0]["bulleted_list_item"]["children"]
        self.assertEqual(len(enfants), 1)
        self.assertEqual(plain(enfants[0]["bulleted_list_item"]["rich_text"]), "enfant")
        self.assertNotIn("children", blocks[1]["bulleted_list_item"])

    def test_trois_niveaux(self):
        blocks, _ = markdown_to_blocks("- a\n  - b\n    - c")
        niveau2 = blocks[0]["bulleted_list_item"]["children"]
        niveau3 = niveau2[0]["bulleted_list_item"]["children"]
        self.assertEqual(plain(niveau3[0]["bulleted_list_item"]["rich_text"]), "c")

    def test_profondeur_excessive_rattachee_au_dernier_niveau_autorise(self):
        blocks, _ = markdown_to_blocks("- a\n  - b\n    - c\n      - d\n        - e")
        niveau2 = blocks[0]["bulleted_list_item"]["children"]
        niveau3 = niveau2[0]["bulleted_list_item"]["children"]
        # d et e ne creusent pas plus loin : Notion n'accepte que deux niveaux d'enfants.
        self.assertEqual([plain(b["bulleted_list_item"]["rich_text"]) for b in niveau3],
                         ["c", "d", "e"])
        self.assertNotIn("children", niveau3[0]["bulleted_list_item"])

    def test_retour_au_niveau_parent(self):
        blocks, _ = markdown_to_blocks("- a\n  - b\n- c")
        self.assertEqual([plain(b["bulleted_list_item"]["rich_text"]) for b in blocks], ["a", "c"])

    def test_indentation_par_tabulation(self):
        blocks, _ = markdown_to_blocks("- parent\n\t- enfant")
        self.assertEqual(len(blocks), 1)
        self.assertEqual(len(blocks[0]["bulleted_list_item"]["children"]), 1)

    def test_types_de_listes_melanges(self):
        blocks, _ = markdown_to_blocks("- puce\n    1. numerotee\n    - [ ] a faire")
        enfants = blocks[0]["bulleted_list_item"]["children"]
        self.assertEqual([b["type"] for b in enfants], ["numbered_list_item", "to_do"])

    def test_cases_a_cocher_apple_imbriquees(self):
        blocks, _ = markdown_to_blocks("☐ courses\n    ☑ pain\n    ☐ lait")
        enfants = blocks[0]["to_do"]["children"]
        self.assertEqual(len(enfants), 2)
        self.assertTrue(enfants[0]["to_do"]["checked"])

    def test_un_bloc_non_liste_referme_la_liste(self):
        blocks, _ = markdown_to_blocks("- a\n\n## Titre\n\n  - b")
        self.assertEqual([b["type"] for b in blocks],
                         ["bulleted_list_item", "heading_2", "bulleted_list_item"])
        self.assertNotIn("children", blocks[0]["bulleted_list_item"])

    def test_liste_plate_inchangee(self):
        blocks, _ = markdown_to_blocks("- a\n- b\n- c")
        self.assertEqual(len(blocks), 3)
        self.assertTrue(all("children" not in b["bulleted_list_item"] for b in blocks))


class TestFrontMatterEtTitre(unittest.TestCase):
    def test_front_matter(self):
        meta, body = parse_front_matter('---\ntitle: "Ma note"\ntags: [a, b]\n---\ncontenu\n')
        self.assertEqual(meta["title"], "Ma note")
        self.assertEqual(meta["tags"], ["a", "b"])
        self.assertEqual(body.strip(), "contenu")

    def test_sans_front_matter(self):
        meta, body = parse_front_matter("juste du texte")
        self.assertEqual(meta, {})
        self.assertEqual(body, "juste du texte")

    def test_titre_depuis_heading(self):
        titre, corps = split_title_and_body("# Mon titre\n\ncorps", "secours")
        self.assertEqual(titre, "Mon titre")
        self.assertEqual(corps.strip(), "corps")

    def test_titre_depuis_premiere_ligne(self):
        titre, corps = split_title_and_body("Réunion du 3 mai\n\nordre du jour", "secours")
        self.assertEqual(titre, "Réunion du 3 mai")
        self.assertEqual(corps.strip(), "ordre du jour")

    def test_titre_de_secours_si_premiere_ligne_est_un_bloc(self):
        titre, corps = split_title_and_body("- une puce\n- une autre", "nom-fichier")
        self.assertEqual(titre, "nom-fichier")
        self.assertEqual(corps, "- une puce\n- une autre")


class TestReadNotes(unittest.TestCase):
    def test_lecture_recursive_et_metadonnees(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Travail").mkdir()
            (root / "Travail" / "reunion.md").write_text("Réunion NOC\n\n- point 1\n", encoding="utf-8")
            (root / "idee.txt").write_text("Idée peinture\n\nCongo + fractales\n", encoding="utf-8")
            (root / "README.md").write_text("à ignorer", encoding="utf-8")
            (root / ".DS_Store").write_text("", encoding="utf-8")

            notes = read_notes(root)
            titres = sorted(n.title for n in notes)
            self.assertEqual(titres, ["Idée peinture", "Réunion NOC"])

            reunion = next(n for n in notes if n.title == "Réunion NOC")
            self.assertEqual(reunion.folder, "Travail")
            self.assertEqual(reunion.body, "- point 1")

            racine = next(n for n in notes if n.title == "Idée peinture")
            self.assertEqual(racine.folder, "")

    def test_empreinte_stable_et_sensible_au_contenu(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fichier = root / "note.md"
            fichier.write_text("Titre\n\ncorps", encoding="utf-8")
            avant = read_notes(root)[0].fingerprint
            self.assertEqual(avant, read_notes(root)[0].fingerprint)
            fichier.write_text("Titre\n\ncorps modifié", encoding="utf-8")
            self.assertNotEqual(avant, read_notes(root)[0].fingerprint)


class TestBuildProperties(unittest.TestCase):
    def _note(self, **kwargs):
        from apple_notes_to_notion import Note
        defaults = dict(path=Path("x.md"), relative_path="Travail/x.md", folder="Travail",
                        title="Ma note", body="", meta={}, modified="2026-05-03")
        defaults.update(kwargs)
        return Note(**defaults)

    def test_titre_toujours_present(self):
        props = build_properties({}, "Name", self._note(), {})
        self.assertEqual(props["Name"]["title"][0]["text"]["content"], "Ma note")

    def test_mapping_selon_le_type_de_propriete(self):
        schema = {
            "Dossier": {"type": "select"},
            "Source": {"type": "multi_select"},
            "Chemin": {"type": "rich_text"},
            "Date": {"type": "date"},
        }
        mapping = {"folder": "Dossier", "source": "Source", "path": "Chemin", "modified": "Date"}
        props = build_properties(schema, "Name", self._note(), mapping)
        self.assertEqual(props["Dossier"]["select"]["name"], "Travail")
        self.assertEqual(props["Source"]["multi_select"][0]["name"], "Apple Notes")
        self.assertEqual(props["Chemin"]["rich_text"][0]["text"]["content"], "Travail/x.md")
        self.assertEqual(props["Date"]["date"]["start"], "2026-05-03")

    def test_propriete_absente_du_schema_ignoree(self):
        props = build_properties({}, "Name", self._note(), {"folder": "Inexistante"})
        self.assertNotIn("Inexistante", props)

    def test_dossier_racine_par_defaut(self):
        props = build_properties({"Dossier": {"type": "select"}}, "Name",
                                 self._note(folder=""), {"folder": "Dossier"})
        self.assertEqual(props["Dossier"]["select"]["name"], "Sans dossier")


if __name__ == "__main__":
    unittest.main()
