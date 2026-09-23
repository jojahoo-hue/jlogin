// Génère la version .docx du manuscrit à partir du markdown assemblé.
//
// Usage :
//   npm install docx            (une seule fois, dans ce dossier ou globalement)
//   node tools/md-to-docx.js    (depuis le dossier livre/)
//
// Entrée  : LA-GRAINE-ET-LES-RACINES.md
// Sortie  : LA-GRAINE-ET-LES-RACINES.docx
//
// Les passages [à enrichir : ...] sont surlignés (fond jaune) et mis en italique
// pour que l'auteur les repère immédiatement.

const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  PageBreak, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  Header, Footer, PageNumber, convertInchesToTwip,
} = require('docx');

const SRC = path.join(__dirname, '..', 'LA-GRAINE-ET-LES-RACINES.md');
const OUT = path.join(__dirname, '..', 'LA-GRAINE-ET-LES-RACINES.docx');

const BODY_FONT = 'Georgia';
const CONTENT_WIDTH = 8500; // A4 moins les marges, en DXA

// ---------------------------------------------------------------- inline runs

function runs(text, base = {}) {
  const out = [];
  const re = /\[à enrichir[^\]]*\]|\*\*([^*]+)\*\*/g;
  let last = 0;
  let m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), ...base }));
    if (m[0].startsWith('[à enrichir')) {
      out.push(new TextRun({ text: m[0], italics: true, bold: true, color: '8A5A00',
        shading: { type: ShadingType.CLEAR, fill: 'FFF0A8' }, ...base }));
    } else {
      out.push(new TextRun({ text: m[1], bold: true, ...base }));
    }
    last = m.index + m[0].length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), ...base }));
  return out.length ? out : [new TextRun({ text: '', ...base })];
}

const body = (text, opts = {}) => new Paragraph({
  children: runs(text),
  alignment: AlignmentType.JUSTIFIED,
  spacing: { line: 320, after: 160 },
  ...opts,
});

// ------------------------------------------------------------------- parsing

const raw = fs.readFileSync(SRC, 'utf8').split('\n');
const start = raw.indexOf('---') + 1; // on saute le bloc de titre du markdown
const lines = raw.slice(start);

const children = [];
const toc = [];
let buf = [];

function flush() {
  if (!buf.length) return;
  const text = buf.join(' ').replace(/\s+/g, ' ').trim();
  buf = [];
  if (text) children.push(body(text));
}

function heading(text, level, opts) {
  flush();
  children.push(new Paragraph({ text, heading: level, ...opts }));
}

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  const t = line.trim();

  if (t === '---' || t === '') { flush(); continue; }

  // tableaux markdown
  if (t.startsWith('|')) {
    flush();
    const rows = [];
    while (i < lines.length && lines[i].trim().startsWith('|')) {
      const cells = lines[i].trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map((c) => c.trim());
      if (!/^-+$/.test(cells[0].replace(/-/g, '-'))) rows.push(cells);
      i++;
    }
    i--;
    const clean = rows.filter((r) => !r.every((c) => /^-+$/.test(c)));
    const cols = Math.max(...clean.map((r) => r.length));
    const widths = cols === 2 ? [2800, CONTENT_WIDTH - 2800] : Array(cols).fill(Math.floor(CONTENT_WIDTH / cols));
    children.push(new Table({
      columnWidths: widths,
      rows: clean.map((cells, r) => new TableRow({
        tableHeader: r === 0,
        children: cells.map((c, k) => new TableCell({
          width: { size: widths[k], type: WidthType.DXA },
          shading: r === 0 ? { type: ShadingType.CLEAR, fill: 'EFEAE0' } : undefined,
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [new Paragraph({
            children: runs(c, r === 0 ? { bold: true } : {}),
            spacing: { line: 280 },
          })],
        })),
      })),
    }));
    children.push(new Paragraph({ text: '', spacing: { after: 160 } }));
    continue;
  }

  // listes numérotées (numérotation conservée telle quelle)
  const num = t.match(/^(\d{1,2})\.\s+(.*)$/);
  if (num) {
    flush();
    let text = num[2];
    while (i + 1 < lines.length && lines[i + 1].trim() !== '' && !/^([#|]|\d{1,2}\.\s|-\s)/.test(lines[i + 1].trim())) {
      text += ' ' + lines[++i].trim();
    }
    children.push(body(`${num[1]}. ${text}`, {
      indent: { left: 420, hanging: 280 },
      spacing: { line: 300, after: 80 },
    }));
    continue;
  }

  // puces
  if (/^-\s+/.test(t)) {
    flush();
    let text = t.replace(/^-\s+/, '');
    while (i + 1 < lines.length && lines[i + 1].trim() !== '' && !/^([#|]|\d{1,2}\.\s|-\s)/.test(lines[i + 1].trim())) {
      text += ' ' + lines[++i].trim();
    }
    children.push(body(`•  ${text}`, {
      indent: { left: 420, hanging: 280 },
      spacing: { line: 300, after: 80 },
    }));
    continue;
  }

  // titres
  if (t.startsWith('### ')) { heading(t.slice(4), HeadingLevel.HEADING_4); continue; }
  if (t.startsWith('## ')) { heading(t.slice(3), HeadingLevel.HEADING_3); continue; }
  if (t.startsWith('# ')) {
    const text = t.slice(2);
    const isPart = /^(Partie|Annexe)\b/.test(text);
    flush();
    children.push(new Paragraph({ children: [new PageBreak()] }));
    children.push(new Paragraph({
      text,
      heading: isPart ? HeadingLevel.HEADING_1 : HeadingLevel.HEADING_2,
      alignment: isPart ? AlignmentType.CENTER : AlignmentType.LEFT,
      spacing: isPart ? { before: 1400, after: 600 } : { before: 240, after: 400 },
    }));
    toc.push({ level: isPart ? 1 : 2, text });
    continue;
  }

  buf.push(t);
}
flush();

// --------------------------------------------------------------- pages liminaires

const title = [
  new Paragraph({ text: '', spacing: { before: 2600 } }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 300 },
    children: [new TextRun({ text: 'LA GRAINE ET LES RACINES', bold: true, size: 52, font: BODY_FONT, characterSpacing: 40 })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 120 },
    children: [new TextRun({ text: "Carnet initiatique d'une Rencontre Initiatique Kongo", italics: true, size: 26, font: BODY_FONT })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 1600 },
    children: [new TextRun({ text: 'Guadeloupe, 13 au 24 juillet 2026', italics: true, size: 26, font: BODY_FONT })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 2000 },
    children: [new TextRun({ text: 'Njaho', size: 30, font: BODY_FONT })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: 'Manuscrit de travail, version 1', size: 20, font: BODY_FONT, color: '666666' })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({
      text: 'Les passages surlignés en jaune sont à compléter par l’auteur',
      size: 20, font: BODY_FONT, color: '666666',
    })],
  }),
];

const contents = [
  new Paragraph({ children: [new PageBreak()] }),
  new Paragraph({ text: 'Table des matières', heading: HeadingLevel.HEADING_1, alignment: AlignmentType.CENTER, spacing: { after: 500 } }),
  ...toc.map((e) => new Paragraph({
    spacing: { line: 300, after: e.level === 1 ? 120 : 40, before: e.level === 1 ? 200 : 0 },
    indent: { left: e.level === 1 ? 0 : 400 },
    children: [new TextRun({
      text: e.text,
      bold: e.level === 1,
      size: e.level === 1 ? 24 : 22,
      font: BODY_FONT,
    })],
  })),
];

// ------------------------------------------------------------------- document

const h = (size, opts = {}) => ({
  run: { font: BODY_FONT, size, bold: true, color: '1A1A1A', ...opts.run },
  paragraph: { spacing: { before: 320, after: 200 }, ...opts.paragraph },
});

const doc = new Document({
  creator: 'Njaho',
  title: 'La graine et les racines',
  description: 'Carnet initiatique, RIK Guadeloupe, juillet 2026',
  styles: {
    default: {
      document: {
        run: { font: BODY_FONT, size: 23, color: '1A1A1A' },
        paragraph: { spacing: { line: 320, after: 160 } },
      },
    },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, ...h(40) },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, ...h(32) },
      { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: BODY_FONT, size: 25, bold: true, color: '333333' },
        paragraph: { spacing: { before: 360, after: 140 }, keepNext: true } },
      { id: 'Heading4', name: 'Heading 4', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: BODY_FONT, size: 23, bold: true, italics: true, color: '333333' },
        paragraph: { spacing: { before: 280, after: 120 }, keepNext: true } },
    ],
  },
  sections: [{
    properties: {
      titlePage: true,
      page: {
        margin: {
          top: convertInchesToTwip(1),
          bottom: convertInchesToTwip(1),
          left: convertInchesToTwip(1.18),
          right: convertInchesToTwip(1.18),
        },
      },
    },
    headers: {
      first: new Header({ children: [new Paragraph({ text: '' })] }),
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 300 },
          children: [new TextRun({ text: 'La graine et les racines', size: 18, font: BODY_FONT, color: '888888', italics: true })],
        })],
      }),
    },
    footers: {
      first: new Footer({ children: [new Paragraph({ text: '' })] }),
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, font: BODY_FONT, color: '888888' })],
        })],
      }),
    },
    children: [...title, ...contents, ...children],
  }],
});

Packer.toBuffer(doc).then((b) => {
  fs.writeFileSync(OUT, b);
  console.log(`écrit : ${OUT} (${(b.length / 1024).toFixed(0)} Ko, ${toc.length} entrées de table des matières)`);
});
