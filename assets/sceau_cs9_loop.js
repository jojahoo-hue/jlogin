/**
 * Loop méditative — 75 BPM + C.S=9 (sceau central, 9 phases internes)
 * Gabarit du module "Géométrie Sacrée & Numérologie" (voir SKILL.md).
 *
 * - Durée loop: 9.6s (12 beats à 75 BPM) => seamless
 * - FPS 30 => 288 frames
 * - Pulsation: 75 BPM (beat) ; Phases internes: C.S=9 (micro-modulations + rotation)
 *
 * Exemple calibré pour LOGIN (C.S = 9). À coller dans editor.p5js.org.
 */

const FPS = 30;
const LOOP_SEC = 9.6;
const TOTAL_FRAMES = Math.round(FPS * LOOP_SEC);

const BPM = 75;
const BEAT_SEC = 60 / BPM;                  // 0.8s
const BEATS_PER_LOOP = LOOP_SEC / BEAT_SEC; // 12 beats

const CS = 9; // Code Secret

function setup() {
  createCanvas(900, 900);
  frameRate(FPS);
  strokeCap(ROUND);
  strokeJoin(ROUND);
}

function draw() {
  const f = (frameCount - 1) % TOTAL_FRAMES;
  const u = f / TOTAL_FRAMES; // 0..1 seamless

  const beatPhase = TWO_PI * (BEATS_PER_LOOP * u); // 12 beats
  const csPhase = TWO_PI * (CS * u);               // 9 phases

  const pulse = 0.5 + 0.5 * sin(beatPhase);          // 75 bpm
  const csWave = 0.5 + 0.5 * sin(csPhase - HALF_PI); // 9 phases

  background(6, 8, 14);
  translate(width / 2, height / 2);
  rotate(0.12 * sin(csPhase)); // alignement doux piloté par C.S

  const phi = TWO_PI * u;
  const glowA = 16 + 26 * pulse + 14 * csWave;
  const glowW = 9 + 7 * csWave;

  noFill();
  for (let i = 0; i < 3; i++) {
    stroke(255, 190, 90, glowA - i * 7);
    strokeWeight(glowW - i * 2.8);
    drawSeal(phi, 1.0 + i * 0.006, csWave);
  }

  stroke(255, 185, 85, 220);
  strokeWeight(2.2);
  drawSeal(phi, 1.0, csWave);

  noStroke();
  fill(255, 245, 235, 190 + 45 * pulse);
  circle(0, 0, 7 + 8 * csWave);

  // (option export) — décommenter pour générer 288 PNG :
  // if (frameCount <= TOTAL_FRAMES) saveCanvas(`frame_${nf(frameCount, 4)}`, 'png');
  // if (frameCount === TOTAL_FRAMES) noLoop();
}

function drawSeal(phi, scaleMul, csWave) {
  beginShape();
  const aMax = TWO_PI * 3;
  const baseScale = 110;
  const aStruct = 0.18 + 0.09 * csWave; // sin(4θ)
  const aCycle = 0.10 + 0.06 * csWave;  // sin(12θ)

  for (let a = 0; a <= aMax; a += 0.01) {
    const rNorm =
      1 +
      aStruct * sin(4 * a + phi) +
      aCycle * sin(12 * a - 0.55 * phi) +
      0.08 * a;
    const r = baseScale * rNorm * scaleMul;
    const wobble = 1 + 0.012 * sin(9 * a + 2.0 * phi); // signature C.S=9
    const rr = r * wobble;
    vertex(rr * cos(a), rr * sin(a));
  }
  endShape();
}
