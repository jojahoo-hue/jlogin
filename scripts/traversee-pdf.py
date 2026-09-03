#!/usr/bin/env python3
"""
traversee-pdf.py — Génère la ressource PDF « La traversée », le déroulé rituel
en cinq mouvements tiré du storyboard Pleine Lune en Poissons.

Usage :
    python3 scripts/traversee-pdf.py [fichier_de_sortie.pdf]

Sortie par défaut : reports/site/la-traversee.pdf

Le document est conçu pour être imprimé en A4 recto seul : fond blanc, filets
sobres, dernière page à remplir à la main. Seule la couverture est en aplat.
"""

import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, KeepTogether, NextPageTemplate, PageBreak,
    PageTemplate, Paragraph, Spacer, Table, TableStyle,
)

# --- Palette, reprise de la direction visuelle du storyboard ----------------
BLEU_NUIT = colors.HexColor("#131A2E")
INDIGO = colors.HexColor("#1F2B4D")
OR = colors.HexColor("#B8860F")
OR_CLAIR = colors.HexColor("#D9B45B")
TERRE = colors.HexColor("#8C3A2B")
ENCRE = colors.HexColor("#22262F")
GRIS = colors.HexColor("#6A7180")
FILET = colors.HexColor("#D3D7DF")

MARGE = 24 * mm
LARGEUR, HAUTEUR = A4


# --- Styles -----------------------------------------------------------------
def styles():
    base = ParagraphStyle(
        "base", fontName="Times-Roman", fontSize=10.5, leading=16,
        textColor=ENCRE, alignment=TA_JUSTIFY, spaceAfter=7,
    )
    return {
        "corps": base,
        "titre_couv": ParagraphStyle(
            "titre_couv", parent=base, fontName="Times-Roman", fontSize=34,
            leading=38, textColor=colors.white, alignment=TA_CENTER,
            spaceAfter=0,
        ),
        "soustitre_couv": ParagraphStyle(
            "soustitre_couv", parent=base, fontName="Times-Italic", fontSize=13,
            leading=20, textColor=OR_CLAIR, alignment=TA_CENTER,
        ),
        "surtitre_couv": ParagraphStyle(
            "surtitre_couv", parent=base, fontName="Helvetica", fontSize=8.5,
            leading=14, textColor=OR_CLAIR, alignment=TA_CENTER,
        ),
        "note_couv": ParagraphStyle(
            "note_couv", parent=base, fontName="Helvetica", fontSize=8,
            leading=13, textColor=colors.HexColor("#8B93A6"),
            alignment=TA_CENTER,
        ),
        "h1": ParagraphStyle(
            "h1", parent=base, fontName="Times-Bold", fontSize=19, leading=24,
            textColor=BLEU_NUIT, alignment=0, spaceBefore=4, spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base, fontName="Times-Bold", fontSize=13, leading=18,
            textColor=INDIGO, alignment=0, spaceBefore=14, spaceAfter=5,
        ),
        "eyebrow": ParagraphStyle(
            "eyebrow", parent=base, fontName="Helvetica", fontSize=7.5,
            leading=12, textColor=OR, alignment=0, spaceAfter=2,
        ),
        "mouvement": ParagraphStyle(
            "mouvement", parent=base, fontName="Times-Bold", fontSize=12,
            leading=16, textColor=TERRE, alignment=0, spaceAfter=3,
        ),
        "duree": ParagraphStyle(
            "duree", parent=base, fontName="Helvetica", fontSize=7.5,
            leading=11, textColor=GRIS, alignment=2, spaceAfter=0,
        ),
        "mantra": ParagraphStyle(
            "mantra", parent=base, fontName="Times-Italic", fontSize=12.5,
            leading=23, textColor=BLEU_NUIT, alignment=TA_CENTER,
            spaceAfter=11,
        ),
        "avert": ParagraphStyle(
            "avert", parent=base, fontName="Times-Roman", fontSize=9.5,
            leading=15, textColor=ENCRE, alignment=TA_JUSTIFY, spaceAfter=5,
        ),
        "champ": ParagraphStyle(
            "champ", parent=base, fontName="Helvetica", fontSize=8.5,
            leading=13, textColor=INDIGO, alignment=0, spaceAfter=1,
        ),
        "pied": ParagraphStyle(
            "pied", parent=base, fontName="Helvetica", fontSize=7.5,
            leading=11, textColor=GRIS, alignment=TA_CENTER,
        ),
    }


# --- Fonds de page ----------------------------------------------------------
def fond_couverture(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BLEU_NUIT)
    canvas.rect(0, 0, LARGEUR, HAUTEUR, stroke=0, fill=1)

    # Lune voilée, haut de page
    cx, cy, r = LARGEUR / 2, HAUTEUR - 62 * mm, 21 * mm
    canvas.setFillColor(colors.HexColor("#26314F"))
    canvas.circle(cx, cy, r, stroke=0, fill=1)
    canvas.setFillColor(colors.HexColor("#33405F"))
    canvas.circle(cx + 3 * mm, cy + 2 * mm, r - 3 * mm, stroke=0, fill=1)

    # Ligne lune, coeur, pieds, terre. Deux segments, pour ne pas traverser
    # le bloc de titre qui occupe le milieu de la page.
    canvas.setStrokeColor(OR)
    canvas.setLineWidth(0.5)
    canvas.line(cx, cy - r - 4 * mm, cx, cy - r - 18 * mm)
    canvas.line(cx, 68 * mm, cx, 46 * mm)

    # Rive : eau à gauche, terre à droite
    canvas.setStrokeColor(INDIGO)
    canvas.setLineWidth(0.7)
    canvas.line(MARGE, 46 * mm, LARGEUR / 2, 46 * mm)
    canvas.setStrokeColor(TERRE)
    canvas.line(LARGEUR / 2, 46 * mm, LARGEUR - MARGE, 46 * mm)

    canvas.restoreState()


def fond_interieur(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(colors.white)
    canvas.rect(0, 0, LARGEUR, HAUTEUR, stroke=0, fill=1)

    # Filet supérieur et titre courant
    canvas.setStrokeColor(FILET)
    canvas.setLineWidth(0.5)
    canvas.line(MARGE, HAUTEUR - 17 * mm, LARGEUR - MARGE, HAUTEUR - 17 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(GRIS)
    canvas.drawString(MARGE, HAUTEUR - 15 * mm, "LA TRAVERSÉE")
    canvas.drawRightString(LARGEUR - MARGE, HAUTEUR - 15 * mm,
                           "Cinq mouvements")

    # Pied de page
    canvas.line(MARGE, 17 * mm, LARGEUR - MARGE, 17 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(MARGE, 12 * mm,
                      "Le symbole soutient l'introspection. "
                      "Il ne remplace ni le fait, ni le consentement, "
                      "ni la décision.")
    canvas.drawRightString(LARGEUR - MARGE, 12 * mm, str(doc.page - 1))
    canvas.restoreState()


# --- Blocs de contenu -------------------------------------------------------
def encadre(texte, s, couleur=OR, fond=colors.HexColor("#FBF7EC")):
    """Encadré à filet latéral, pour les avertissements et rappels."""
    p = Paragraph(texte, s["avert"])
    t = Table([[p]], colWidths=[LARGEUR - 2 * MARGE])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), fond),
        ("LINEBEFORE", (0, 0), (0, -1), 2, couleur),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t


def etape(numero, titre, duree, corps, s):
    """Une étape du déroulé : numéro doré, titre, durée à droite, texte."""
    entete = Table(
        [[Paragraph(f'<font color="#B8860F">{numero}</font>  {titre}',
                    s["mouvement"]),
          Paragraph(duree, s["duree"])]],
        colWidths=[(LARGEUR - 2 * MARGE) * 0.78, (LARGEUR - 2 * MARGE) * 0.22],
    )
    entete.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, FILET),
    ]))
    # KeepTogether : un titre d'étape seul en bas de page, sans son texte,
    # casse la lecture d'un déroulé qu'on suit pas à pas.
    return [KeepTogether([entete, Spacer(1, 5), Paragraph(corps, s["corps"])]),
            Spacer(1, 9)]


def champ_a_remplir(libelle, s, lignes=2):
    """Un champ de la fiche d'intégration, avec ses lignes d'écriture."""
    blocs = [Paragraph(libelle, s["champ"])]
    largeur = LARGEUR - 2 * MARGE
    for _ in range(lignes):
        t = Table([[""]], colWidths=[largeur], rowHeights=[9 * mm])
        t.setStyle(TableStyle([
            ("LINEBELOW", (0, 0), (-1, -1), 0.4, FILET),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))
        blocs.append(t)
    # Assez d'air pour que le libellé suivant se rattache visuellement à ses
    # propres lignes, et non à celles du champ précédent.
    blocs.append(Spacer(1, 13))
    return blocs


# --- Document ---------------------------------------------------------------
def construire(sortie):
    s = styles()
    doc = BaseDocTemplate(
        str(sortie), pagesize=A4,
        leftMargin=MARGE, rightMargin=MARGE,
        topMargin=26 * mm, bottomMargin=24 * mm,
        title="La traversée, rituel en cinq mouvements",
        author="Njaho", subject="Ki TUNI",
    )

    cadre_couv = Frame(MARGE, 55 * mm, LARGEUR - 2 * MARGE, HAUTEUR - 135 * mm,
                       id="couv", showBoundary=0)
    cadre_int = Frame(MARGE, 24 * mm, LARGEUR - 2 * MARGE, HAUTEUR - 50 * mm,
                      id="int", showBoundary=0)
    doc.addPageTemplates([
        PageTemplate(id="couverture", frames=[cadre_couv],
                     onPage=fond_couverture),
        PageTemplate(id="interieur", frames=[cadre_int],
                     onPage=fond_interieur),
    ])

    h = []

    # --- Couverture ---------------------------------------------------------
    h.append(Spacer(1, 16 * mm))
    h.append(Paragraph("NZA NGA DIA KI TUNI", s["surtitre_couv"]))
    h.append(Spacer(1, 6))
    h.append(Paragraph("La traversée", s["titre_couv"]))
    h.append(Spacer(1, 8))
    h.append(Paragraph("Un rituel sobre en cinq mouvements",
                       s["soustitre_couv"]))
    h.append(Spacer(1, 5))
    h.append(Paragraph("De l'émotion à l'incarnation", s["soustitre_couv"]))
    # Descend la note près de la rive, sinon la moitié basse de la couverture
    # reste vide et la composition bascule vers le haut.
    h.append(Spacer(1, 58 * mm))
    h.append(Paragraph(
        "Ce document ne promet aucun phénomène et n'annonce aucun avenir.<br/>"
        "Il ordonne la conscience, et il se ferme.", s["note_couv"]))

    h.append(NextPageTemplate("interieur"))
    h.append(PageBreak())

    # --- Avant de commencer -------------------------------------------------
    h.append(Paragraph("AVANT DE COMMENCER", s["eyebrow"]))
    h.append(Paragraph("Ce que ce rituel est, et ce qu'il n'est pas", s["h1"]))

    h.append(Paragraph(
        "La Takia ne cherche pas à produire un phénomène. Elle ordonne la "
        "conscience en cinq mouvements : nommer, purifier, discerner, incarner "
        "et rayonner. Ce qu'elle produit se vérifie le lendemain, dans le "
        "sommeil, le budget, la parole donnée et le premier geste choisi. Pas "
        "pendant.", s["corps"]))

    h.append(Paragraph(
        "Rien ici ne demande de croire à quoi que ce soit. Le symbole soutient "
        "l'introspection : il ne remplace ni les faits, ni le consentement des "
        "personnes concernées, ni votre décision responsable. Si une image vous "
        "vient et qu'elle contredit un fait vérifiable, c'est le fait qui "
        "compte.", s["corps"]))

    h.append(Spacer(1, 6))
    h.append(encadre(
        "<b>Sécurité.</b> Le rituel peut se faire près d'une eau calme "
        "uniquement si le lieu est sûr, accessible et autorisé. La nuit, rester "
        "loin des berges glissantes et ne pas entrer dans l'eau. Ne jamais "
        "brûler de papier près de la végétation : déchirer suffit. Une bougie "
        "n'est pas nécessaire, une lampe convient et ne met le feu à rien.",
        s, couleur=TERRE, fond=colors.HexColor("#FBF1EE")))

    h.append(Paragraph("Ce qu'il faut préparer", s["h2"]))
    materiel = [
        ["Un tissu bleu nuit", "Pour poser les objets, et délimiter l'espace"],
        ["Une lampe stable", "Allumée au cinquième mouvement seulement"],
        ["Une plume ou une feuille blanche", "Elle représente l'intention"],
        ["Une pierre sombre", "Elle représente les conséquences"],
        ["Une feuille et un stylo", "L'écriture fait la moitié du travail"],
        ["Un bol d'eau", "Pour le deuxième mouvement"],
        ["Un verre d'eau", "Distinct du bol, pour boire à la fermeture"],
    ]
    t = Table(materiel, colWidths=[(LARGEUR - 2 * MARGE) * 0.42,
                                   (LARGEUR - 2 * MARGE) * 0.58])
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (0, -1), "Times-Bold", 9.5),
        ("FONT", (1, 0), (1, -1), "Times-Roman", 9.5),
        ("TEXTCOLOR", (0, 0), (0, -1), INDIGO),
        ("TEXTCOLOR", (1, 0), (1, -1), GRIS),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, FILET),
    ]))
    h.append(t)
    h.append(Spacer(1, 8))
    h.append(Paragraph(
        "Téléphone en silencieux. Vérifier le sol et les accès avant de "
        "commencer. Compter entre trente-cinq et cinquante minutes, sans "
        "contrainte d'horaire derrière.", s["corps"]))

    h.append(PageBreak())

    # --- Le déroulé ---------------------------------------------------------
    h.append(Paragraph("LE DÉROULÉ", s["eyebrow"]))
    h.append(Paragraph("Neuf étapes, cinq mouvements", s["h1"]))

    for args in [
        ("1", "Préparer", "5 min",
         "Disposer le tissu, la lampe éteinte, la plume, la pierre, le bol "
         "d'eau, le verre, la feuille et le stylo. Vérifier le sol et les "
         "accès. Mettre le téléphone en silencieux."),
        ("2", "Ouvrir", "3 min",
         "Sentir les pieds. Nommer à voix basse le lieu, la date et "
         "l'intention. Trois expirations lentes, confortables, sans rétention "
         "ni hyperventilation."),
        ("3", "Écouter", "5 min",
         "Regarder le reflet de la lune, ou son image. Accueillir ce qui vient "
         "sans chercher de signe. Noter seulement les mots essentiels, pas des "
         "phrases."),
    ]:
        h.extend(etape(*args, s))

    h.append(Spacer(1, 4))
    h.append(Paragraph("Les cinq mouvements de la Takia", s["h2"]))

    for args in [
        ("4", "NTETE, nommer", "5 min",
         "Écrire deux phrases, et les lire à voix haute : « Je cesse de… » puis "
         "« Je choisis d'incarner… ». Poser la plume sur la première, la pierre "
         "sur la seconde. Tant qu'une chose n'est pas nommée, elle continue de "
         "gouverner sans être vue."),
        ("5", "ZOLE, purifier", "5 min",
         "Toucher l'eau du bol, ou se laver les mains. Nommer une charge qui "
         "ne vous appartient pas et la rendre à qui de droit : « je te laisse "
         "décider de cela ». Nommer l'enseignement que vous conservez. Déchirer "
         "la feuille si vous le souhaitez. Ne rien brûler."),
        ("6", "TATU, discerner", "7 min",
         "Prendre une décision réelle, en cours, et la peser : quel fait la "
         "justifie, qui sera affecté, quel coût, qui doit y consentir, quelle "
         "limite évite la domination, et quelle version plus petite serait "
         "possible. C'est le mouvement le plus long, et celui qu'on saute le "
         "plus souvent."),
        ("7", "YA, incarner", "5 min",
         "Écrire un acte réalisable dans les vingt-quatre heures, avec son "
         "premier geste, sa durée et son critère de fin. Un acte sans critère "
         "de fin n'est pas un acte, c'est une intention."),
        ("8", "TANU, rayonner", "4 min",
         "Allumer la lampe ou la rapprocher. Lire le mantra de la page "
         "suivante. Formuler une offre simple : « voici ce que je peux faire, "
         "dans cette limite, si cela vous convient »."),
        ("9", "Fermer", "3 min",
         "Boire le verre d'eau. Ranger les objets. Nommer trois choses "
         "visibles autour de vous. Reprendre une activité ordinaire."),
    ]:
        h.extend(etape(*args, s))

    h.append(Spacer(1, 4))
    h.append(encadre(
        "<b>La fermeture compte autant que l'ouverture.</b> Ne pas poursuivre "
        "l'analyse cette nuit-là. Une pratique qui ne se ferme jamais devient "
        "une rumination, et la rumination défait ce que le discernement avait "
        "construit.", s))

    h.append(PageBreak())

    # --- Mantra -------------------------------------------------------------
    h.append(Paragraph("HUITIÈME ÉTAPE", s["eyebrow"]))
    h.append(Paragraph("Mantra de passage", s["h1"]))
    h.append(Paragraph(
        "Lire lentement, une phrase par expiration confortable. Laisser un "
        "silence après chaque groupe de deux phrases. Cette parole n'est pas "
        "une formule qui agit : elle rappelle les choix que l'acte devra "
        "confirmer demain.", s["corps"]))
    h.append(Spacer(1, 14))

    lignes = [
        "Je rends à chacun ce qui relève de son chemin.",
        "Je reconnais mes manquements sans devenir leur prisonnier.",
        "Je ne confonds plus intuition et certitude,",
        "amour et sauvetage, protection et domination.",
        "J'accueille le symbole sans lui remettre mon pouvoir.",
        "J'unis le spirituel au concret par une parole digne,",
        "une limite juste et un acte responsable.",
        "Ce qui se clôt devient enseignement.",
        "Ce qui demeure devient engagement.",
    ]
    corps_mantra = [[Paragraph(l, s["mantra"])] for l in lignes]
    t = Table(corps_mantra, colWidths=[LARGEUR - 2 * MARGE])
    t.setStyle(TableStyle([
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("LINEABOVE", (0, 0), (-1, 0), 0.7, OR),
        ("LINEBELOW", (0, -1), (-1, -1), 0.7, OR),
        ("TOPPADDING", (0, 0), (-1, 0), 18),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 18),
    ]))
    h.append(t)
    h.append(Spacer(1, 14))
    h.append(Paragraph("Puis garder une minute de silence.", s["corps"]))

    h.append(PageBreak())

    # --- Fiche d'intégration ------------------------------------------------
    h.append(Paragraph("APRÈS LA TRAVERSÉE", s["eyebrow"]))
    h.append(Paragraph("Fiche d'intégration", s["h1"]))
    h.append(Paragraph(
        "À remplir à la main, le lendemain plutôt que le soir même. Les quatre "
        "premières lignes séparent ce que nous confondons toujours : le fait, "
        "le ressenti, l'image et l'histoire que nous y ajoutons.", s["corps"]))
    h.append(Spacer(1, 8))

    for libelle, n in [
        ("LE FAIT OBSERVABLE LE PLUS MARQUANT", 2),
        ("L'ÉMOTION ET SA LOCALISATION DANS LE CORPS", 1),
        ("L'IMAGE SYMBOLIQUE, SANS LUI ATTRIBUER D'AUTORITÉ", 1),
        ("L'INTERPRÉTATION QUE J'AI AJOUTÉE", 2),
        ("L'ENSEIGNEMENT RETENU", 2),
        ("L'ACTE OBSERVABLE PRÉVU DANS LES VINGT-QUATRE HEURES", 2),
        ("LA LIMITE OU LE CONSENTEMENT À VÉRIFIER", 1),
    ]:
        h.extend(champ_a_remplir(libelle, s, n))

    h.append(Spacer(1, 4))
    h.append(Paragraph("ANCRAGE, CLARTÉ, LIMITES, SERVICE, DE 0 À 4",
                       s["champ"]))
    largeur_col = (LARGEUR - 2 * MARGE) / 4
    notes = Table(
        [["Ancrage", "Clarté", "Limites", "Service"], ["", "", "", ""]],
        colWidths=[largeur_col] * 4, rowHeights=[7 * mm, 13 * mm])
    notes.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), "Helvetica", 8),
        ("TEXTCOLOR", (0, 0), (-1, 0), GRIS),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
        ("BOX", (0, 1), (-1, 1), 0.4, FILET),
        ("INNERGRID", (0, 1), (-1, 1), 0.4, FILET),
    ]))
    h.append(notes)

    doc.build(h)
    return sortie


if __name__ == "__main__":
    defaut = Path(__file__).resolve().parent.parent / "reports/site/la-traversee.pdf"
    cible = Path(sys.argv[1]) if len(sys.argv) > 1 else defaut
    cible.parent.mkdir(parents=True, exist_ok=True)
    chemin = construire(cible)
    print(f"PDF généré : {chemin}")
