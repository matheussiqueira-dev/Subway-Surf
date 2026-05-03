const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const scoreValue = document.getElementById("scoreValue");
const coinValue = document.getElementById("coinValue");
const lifeValue = document.getElementById("lifeValue");
const startOverlay = document.getElementById("startOverlay");
const startBtn = document.getElementById("startBtn");
const gestureBridge = document.getElementById("gestureBridge");

const laneCount = 3;
const state = {
  width: 0,
  height: 0,
  dpr: 1,
  running: false,
  gameOver: false,
  lane: 1,
  targetLane: 1,
  playerX: 0,
  playerY: 0,
  velocityY: 0,
  slideUntil: 0,
  shieldUntil: 0,
  shieldCooldownUntil: 0,
  invincibleUntil: 0,
  speed: 380,
  score: 0,
  coins: 0,
  lives: 3,
  distance: 0,
  nextSpawn: 0,
  items: [],
  particles: [],
  lastTelemetryTimestamp: "",
  lastTime: 0,
};

function resize() {
  state.dpr = Math.max(1, Math.min(2, window.devicePixelRatio || 1));
  state.width = window.innerWidth;
  state.height = window.innerHeight;
  canvas.width = Math.floor(state.width * state.dpr);
  canvas.height = Math.floor(state.height * state.dpr);
  canvas.style.width = `${state.width}px`;
  canvas.style.height = `${state.height}px`;
  ctx.setTransform(state.dpr, 0, 0, state.dpr, 0, 0);
  state.playerY = groundY();
  state.playerX = laneX(state.targetLane);
}

function groundY() {
  return state.height * 0.76;
}

function laneX(lane) {
  const center = state.width / 2;
  const laneWidth = Math.min(180, state.width * 0.22);
  return center + (lane - 1) * laneWidth;
}

function resetGame() {
  Object.assign(state, {
    running: true,
    gameOver: false,
    lane: 1,
    targetLane: 1,
    playerX: laneX(1),
    playerY: groundY(),
    velocityY: 0,
    slideUntil: 0,
    shieldUntil: 0,
    shieldCooldownUntil: 0,
    invincibleUntil: 0,
    speed: 380,
    score: 0,
    coins: 0,
    lives: 3,
    distance: 0,
    nextSpawn: 450,
    items: [],
    particles: [],
    lastTelemetryTimestamp: "",
  });
  startOverlay.classList.add("hidden");
  canvas.focus();
}

function clampLane(lane) {
  return Math.max(0, Math.min(laneCount - 1, lane));
}

function command(action) {
  if (!state.running || state.gameOver) {
    if (action === "jump" || action === "hoverboard" || action === "start") {
      resetGame();
    }
    return;
  }

  if (action === "left") state.targetLane = clampLane(state.targetLane - 1);
  if (action === "right") state.targetLane = clampLane(state.targetLane + 1);
  if (action === "jump" && isGrounded()) state.velocityY = -780;
  if (action === "slide" && isGrounded()) state.slideUntil = performance.now() + 520;
  if (action === "hoverboard" && performance.now() > state.shieldCooldownUntil) {
    state.shieldUntil = performance.now() + 4800;
    state.shieldCooldownUntil = performance.now() + 10000;
    burst(state.playerX, state.playerY - 52, "#20e0a4", 26);
  }
}

function isGrounded() {
  return state.playerY >= groundY() - 0.5;
}

function keyToAction(event) {
  const key = event.key.toLowerCase();
  if (key === "arrowleft" || key === "a") return "left";
  if (key === "arrowright" || key === "d") return "right";
  if (key === "arrowup" || key === "w") return "jump";
  if (key === "arrowdown" || key === "s") return "slide";
  if (key === " " || key === "h") return "hoverboard";
  if (key === "enter") return "start";
  if (key === "r" && state.gameOver) return "start";
  return "";
}

window.addEventListener("keydown", (event) => {
  const action = keyToAction(event);
  if (!action) return;
  event.preventDefault();
  command(action);
});

document.querySelectorAll("[data-action]").forEach((button) => {
  const action = button.getAttribute("data-action");
  button.addEventListener("pointerdown", (event) => {
    event.preventDefault();
    command(action);
  });
});

startBtn.addEventListener("click", () => command("start"));
canvas.addEventListener("pointerdown", () => {
  canvas.focus();
});
window.addEventListener("resize", resize);

function spawnItem() {
  const lane = Math.floor(Math.random() * 3);
  const roll = Math.random();
  const type = roll > 0.74 ? "gate" : roll > 0.36 ? "barrier" : "coin";
  state.items.push({
    type,
    lane,
    z: state.height + 120,
    wobble: Math.random() * Math.PI * 2,
    consumed: false,
  });

  if (Math.random() > 0.45) {
    state.items.push({
      type: "coin",
      lane: Math.floor(Math.random() * 3),
      z: state.height + 280 + Math.random() * 160,
      wobble: Math.random() * Math.PI * 2,
      consumed: false,
    });
  }
}

function update(dt) {
  if (!state.running || state.gameOver) return;

  const now = performance.now();
  state.speed = Math.min(660, state.speed + dt * 9);
  state.distance += state.speed * dt;
  state.score += dt * state.speed * 0.06;
  state.nextSpawn -= state.speed * dt;
  if (state.nextSpawn <= 0) {
    spawnItem();
    state.nextSpawn = Math.max(260, 620 - state.speed * 0.34);
  }

  const targetX = laneX(state.targetLane);
  state.playerX += (targetX - state.playerX) * Math.min(1, dt * 13);
  if (Math.abs(state.playerX - targetX) < 2) state.lane = state.targetLane;

  state.velocityY += 2100 * dt;
  state.playerY += state.velocityY * dt;
  if (state.playerY > groundY()) {
    state.playerY = groundY();
    state.velocityY = 0;
  }

  state.items.forEach((item) => {
    item.z -= state.speed * dt;
    item.wobble += dt * 4;
    if (!item.consumed && collides(item)) resolveCollision(item, now);
  });
  state.items = state.items.filter((item) => item.z > -100 && !item.remove);

  state.particles.forEach((particle) => {
    particle.x += particle.vx * dt;
    particle.y += particle.vy * dt;
    particle.life -= dt;
  });
  state.particles = state.particles.filter((particle) => particle.life > 0);
}

function collides(item) {
  const ix = laneX(item.lane);
  const iy = item.z;
  const playerTop = isSliding() ? state.playerY - 48 : state.playerY - 118;
  const playerBottom = state.playerY;
  const closeX = Math.abs(ix - state.playerX) < 54;
  if (!closeX) return false;
  if (item.type === "coin") return Math.abs(iy - (state.playerY - 78)) < 48;
  if (item.type === "gate") return iy > playerTop - 16 && iy < playerBottom - 42;
  return iy > playerTop + 18 && iy < playerBottom + 12;
}

function resolveCollision(item, now) {
  item.consumed = true;
  if (item.type === "coin") {
    state.coins += 1;
    state.score += 160;
    burst(laneX(item.lane), item.z, "#ffc83d", 18);
    item.remove = true;
    return;
  }

  const safeSlide = item.type === "gate" && isSliding();
  const safeShield = now < state.shieldUntil;
  const safeInvincible = now < state.invincibleUntil;
  if (safeSlide || safeShield || safeInvincible) {
    state.score += 90;
    burst(laneX(item.lane), item.z, safeShield ? "#20e0a4" : "#43b9ff", 16);
    item.remove = true;
    return;
  }

  state.lives -= 1;
  state.invincibleUntil = now + 1300;
  burst(laneX(item.lane), item.z, "#ff4d4f", 30);
  item.remove = true;
  if (state.lives <= 0) {
    state.gameOver = true;
    state.running = false;
    startOverlay.classList.remove("hidden");
    startBtn.textContent = "Reiniciar";
  }
}

function isSliding() {
  return performance.now() < state.slideUntil && isGrounded();
}

function burst(x, y, color, amount) {
  for (let i = 0; i < amount; i += 1) {
    const angle = Math.random() * Math.PI * 2;
    const speed = 70 + Math.random() * 180;
    state.particles.push({
      x,
      y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      color,
      life: 0.35 + Math.random() * 0.45,
    });
  }
}

function draw() {
  ctx.clearRect(0, 0, state.width, state.height);
  drawSky();
  drawTrack();
  drawItems();
  drawPlayer();
  drawParticles();
  updateHud();
}

function drawSky() {
  const gradient = ctx.createLinearGradient(0, 0, 0, state.height);
  gradient.addColorStop(0, "#101d2a");
  gradient.addColorStop(0.5, "#1e2731");
  gradient.addColorStop(1, "#0b0d12");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, state.width, state.height);

  ctx.fillStyle = "rgba(255, 200, 61, 0.18)";
  ctx.beginPath();
  ctx.arc(state.width * 0.78, state.height * 0.18, 70, 0, Math.PI * 2);
  ctx.fill();
}

function drawTrack() {
  const horizon = state.height * 0.2;
  const bottom = state.height + 40;
  const center = state.width / 2;
  const halfBottom = Math.min(360, state.width * 0.42);
  const halfTop = Math.min(84, state.width * 0.13);

  ctx.fillStyle = "#20242a";
  ctx.beginPath();
  ctx.moveTo(center - halfTop, horizon);
  ctx.lineTo(center + halfTop, horizon);
  ctx.lineTo(center + halfBottom, bottom);
  ctx.lineTo(center - halfBottom, bottom);
  ctx.closePath();
  ctx.fill();

  for (let i = -1; i <= 1; i += 1) {
    const x = laneX(i + 1);
    const topX = center + (x - center) * 0.22;
    ctx.strokeStyle = i === 0 ? "rgba(255,255,255,0.34)" : "rgba(255,255,255,0.2)";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(topX, horizon);
    ctx.lineTo(x, bottom);
    ctx.stroke();
  }

  const offset = state.distance % 90;
  for (let y = horizon + offset; y < bottom; y += 90) {
    const scale = (y - horizon) / (bottom - horizon);
    ctx.fillStyle = "rgba(255,255,255,0.13)";
    ctx.fillRect(center - halfBottom * scale, y, halfBottom * 2 * scale, 4 + scale * 8);
  }
}

function projectY(z) {
  return z;
}

function itemScale(y) {
  return 0.55 + Math.max(0, y / state.height) * 0.72;
}

function drawItems() {
  state.items.forEach((item) => {
    if (item.consumed) return;
    const x = laneX(item.lane);
    const y = projectY(item.z);
    const scale = itemScale(y);
    if (item.type === "coin") {
      ctx.fillStyle = "#ffc83d";
      ctx.beginPath();
      ctx.ellipse(x, y + Math.sin(item.wobble) * 6, 18 * scale, 24 * scale, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = "rgba(255,255,255,0.62)";
      ctx.lineWidth = 2;
      ctx.stroke();
      return;
    }

    if (item.type === "gate") {
      ctx.fillStyle = "#ff9b2f";
      roundRect(x - 58 * scale, y - 76 * scale, 116 * scale, 28 * scale, 6 * scale);
      ctx.fill();
      ctx.fillStyle = "rgba(0,0,0,0.32)";
      roundRect(x - 46 * scale, y - 66 * scale, 92 * scale, 8 * scale, 4 * scale);
      ctx.fill();
      return;
    }

    ctx.fillStyle = "#ff4d4f";
    roundRect(x - 42 * scale, y - 76 * scale, 84 * scale, 84 * scale, 8 * scale);
    ctx.fill();
    ctx.fillStyle = "rgba(255,255,255,0.22)";
    roundRect(x - 28 * scale, y - 62 * scale, 56 * scale, 14 * scale, 4 * scale);
    ctx.fill();
  });
}

function drawPlayer() {
  const now = performance.now();
  const sliding = isSliding();
  const shield = now < state.shieldUntil;
  const blink = now < state.invincibleUntil && Math.floor(now / 90) % 2 === 0;
  if (blink) return;

  const x = state.playerX;
  const y = state.playerY;
  const width = sliding ? 86 : 64;
  const height = sliding ? 50 : 116;

  if (shield) {
    ctx.strokeStyle = "rgba(32, 224, 164, 0.78)";
    ctx.lineWidth = 5;
    ctx.beginPath();
    ctx.ellipse(x, y - height / 2, width * 0.78, height * 0.72, 0, 0, Math.PI * 2);
    ctx.stroke();
  }

  ctx.fillStyle = shield ? "#20e0a4" : "#43b9ff";
  roundRect(x - width / 2, y - height, width, height, 18);
  ctx.fill();

  ctx.fillStyle = "#f8fbff";
  ctx.beginPath();
  ctx.arc(x - 13, y - height + 30, 5, 0, Math.PI * 2);
  ctx.arc(x + 13, y - height + 30, 5, 0, Math.PI * 2);
  ctx.fill();
}

function drawParticles() {
  state.particles.forEach((particle) => {
    ctx.globalAlpha = Math.max(0, particle.life * 2);
    ctx.fillStyle = particle.color;
    ctx.beginPath();
    ctx.arc(particle.x, particle.y, 4, 0, Math.PI * 2);
    ctx.fill();
  });
  ctx.globalAlpha = 1;
}

function roundRect(x, y, width, height, radius) {
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.lineTo(x + width - radius, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
  ctx.lineTo(x + width, y + height - radius);
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
  ctx.lineTo(x + radius, y + height);
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
  ctx.lineTo(x, y + radius);
  ctx.quadraticCurveTo(x, y, x + radius, y);
  ctx.closePath();
}

function updateHud() {
  scoreValue.textContent = Math.floor(state.score).toString().padStart(6, "0");
  coinValue.textContent = String(state.coins);
  lifeValue.textContent = String(Math.max(0, state.lives));
}

async function pollTelemetry() {
  if (!gestureBridge.checked) return;
  try {
    const response = await fetch("/v1/telemetry?limit=1");
    if (!response.ok) return;
    const data = await response.json();
    const latest = data.latest;
    if (!latest || latest.timestamp === state.lastTelemetryTimestamp) return;
    state.lastTelemetryTimestamp = latest.timestamp;
    const actionMap = {
      LEFT: "left",
      RIGHT: "right",
      JUMP: "jump",
      SLIDE: "slide",
      HOVERBOARD: "hoverboard",
    };
    if (actionMap[latest.action]) command(actionMap[latest.action]);
  } catch {
    // Dashboard can still be played with keyboard/touch while telemetry is offline.
  }
}

function frame(time) {
  const dt = Math.min(0.033, (time - state.lastTime) / 1000 || 0);
  state.lastTime = time;
  update(dt);
  draw();
  requestAnimationFrame(frame);
}

resize();
draw();
requestAnimationFrame(frame);
setInterval(pollTelemetry, 220);
