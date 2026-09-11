/**
 * Roue base 12 — Glyphes + quadripôle respiratoire (C.S=3)
 * Gabarit du module "Géométrie Sacrée & Numérologie" (voir SKILL.md).
 *
 * Loop: 9.6s @30fps => 288 frames (seamless)
 * 75 bpm => 12 battements / loop
 * C.S=3 => 3 respirations / loop ; chaque respiration active 4 glyphes : 0-3, 4-7, 8-11
 *
 * À coller dans editor.p5js.org. Adapter CS, GLYPH_TYPES, GLYPH_TWIST
 * aux lettres réelles du mot traité.
 */

const FPS = 30;
const LOOP_SEC = 9.6;
const TOTAL_FRAMES = Math.round(FPS * LOOP_SEC);

const BPM = 75;
const BEAT_SEC = 60 / BPM;                  // 0.8s
const BEATS_PER_LOOP = LOOP_SEC / BEAT_SEC; // 12
const CS = 3;                               // Code Secret -> respirations / loop

// 12 "glyphes" (segments/angles) : type 0=segment, 1=angle L, 2=chevron, 3=hook
const GLYPH_TYPES = [0, 1, 2, 1, 3, 0, 1, 2, 1, 3, 0, 2];
const GLYPH_TWIST = [0, 20, -15, 35, -30, 10, 25, -20, 15, -10, 30, -25];

function setup() {
  createCanvas(1000, 1000);
  frameRate(FPS);
  strokeCap(ROUND);
  strokeJoin(ROUND);
  textFont('Helvetica');
}

function draw() {
  const f = (frameCount - 1) % TOTAL_FRAMES;
  const u = f / TOTAL_FRAMES; // 0..1 seamless

  const beatPhase = TWO_PI * (BEATS_PER_LOOP * u);
  const breathPhase = TWO_PI * (CS * u);

  const pulse = 0.5 + 0.5 * sin(beatPhase);              // 75 bpm
  const breath = 0.5 + 0.5 * sin(breathPhase - HALF_PI); // respiration

  const breathIndex = Math.floor(CS * u) % CS; // 0..CS-1
  const activeStart = breathIndex * 4;         // 0,4,8

  background(6, 8, 14);
  translate(width / 2, height / 2);

  drawSacredWheelGlyphs(pulse, breath, activeStart);

  const phi = TWO_PI * u;
  drawCentralSeal(phi, pulse, breath);

  noStroke();
  fill(255, 245, 235, 200 + 40 * pulse);
  circle(0, 0, 7 + 6 * breath);

  // (option export) — décommenter pour générer 288 PNG :
  // if (frameCount <= TOTAL_FRAMES) saveCanvas(`frame_${nf(frameCount, 4)}`, 'png');
  // if (frameCount === TOTAL_FRAMES) noLoop();
}

function drawCentralSeal(phi, pulse, breath) {
  noFill();
  for (let i = 0; i < 3; i++) {
    stroke(255, 190, 90, (18 + 24 * pulse) - i * 6);
    strokeWeight((10 + 10 * breath) - i * 3);
    drawSeal(phi, 1.0 + i * 0.006, breath);
  }
  stroke(255, 185, 85, 220);
  strokeWeight(2.2);
  drawSeal(phi, 1.0, breath);
}

function drawSeal(phi, scaleMul, breath) {
  beginShape();
  const aMax = TWO_PI * 3;
  const baseScale = 110;
  const aStruct = 0.18 + 0.10 * breath; // 4θ
  const aCycle = 0.10 + 0.06 * breath;  // 12θ

  for (let a = 0; a <= aMax; a += 0.01) {
    const rNorm =
      1 +
      aStruct * sin(4 * a + phi) +
      aCycle * sin(12 * a - 0.6 * phi) +
      0.08 * a;
    const r = baseScale * rNorm * scaleMul;
    vertex(r * cos(a), r * sin(a));
  }
  endShape();
}

function drawSacredWheelGlyphs(pulse, breath, activeStart) {
  const R = 330;
  const ringAlpha = 70 + 30 * pulse;

  noFill();
  stroke(120, 150, 210, ringAlpha);
  strokeWeight(1);
  circle(0, 0, R * 2);

  for (let i = 0; i < 12; i++) {
    const ang = -HALF_PI + i * TWO_PI / 12;
    const x = R * cos(ang);
    const y = R * sin(ang);

    const isActive = (i >= activeStart && i < activeStart + 4);
    const a = isActive ? (170 + 60 * breath) : (90 + 40 * pulse);
    const w = isActive ? (3.5 + 2.5 * breath) : (2.0 + 1.0 * pulse);
    const col = isActive ? color(255, 200, 110, a) : color(185, 210, 255, a);

    push();
    translate(x, y);
    rotate(ang + radians(GLYPH_TWIST[i]));

    fill(col);
    noStroke();
    circle(0, 0, isActive ? (8 + 6 * pulse) : (6 + 3 * pulse));

    noFill();
    stroke(col);
    strokeWeight(w);
    drawGlyph(GLYPH_TYPES[i], isActive, pulse, breath);
    pop();
  }

  // quadrature (rappel 4 plans)
  const quadAlpha = 25 + 35 * breath;
  stroke(255, 245, 235, quadAlpha);
  strokeWeight(1);
  for (let k = 0; k < 4; k++) {
    const a = -HALF_PI + k * TWO_PI / 4;
    line(0, 0, (R - 40) * cos(a), (R - 40) * sin(a));
  }
}

function drawGlyph(type, isActive, pulse, breath) {
  const L = isActive ? (38 + 12 * breath) : (34 + 8 * pulse);
  switch (type) {
    case 0: // segment
      line(10, 0, 10 + L, 0);
      break;
    case 1: // angle L
      line(10, 0, 10 + L * 0.75, 0);
      line(10 + L * 0.75, 0, 10 + L * 0.75, -L * 0.45);
      break;
    case 2: // chevron
      line(10, 0, 10 + L * 0.55, -L * 0.35);
      line(10 + L * 0.55, -L * 0.35, 10 + L, 0);
      break;
    case 3: // hook
      line(10, 0, 10 + L * 0.65, 0);
      line(10 + L * 0.65, 0, 10 + L * 0.65, L * 0.35);
      break;
  }
}
