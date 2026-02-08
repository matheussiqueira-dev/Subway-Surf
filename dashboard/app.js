const actionBadge = document.getElementById("actionBadge");
const fpsValue = document.getElementById("fpsValue");
const trackingState = document.getElementById("trackingState");
const activeProfile = document.getElementById("activeProfile");
const profilesList = document.getElementById("profilesList");
const profileForm = document.getElementById("profileForm");
const formMessage = document.getElementById("formMessage");
const refreshProfilesBtn = document.getElementById("refreshProfilesBtn");
const saveApiKeyBtn = document.getElementById("saveApiKeyBtn");
const apiKeyInput = document.getElementById("apiKeyInput");
const lastUpdateText = document.getElementById("lastUpdateText");
const sparkline = document.getElementById("fpsSparkline");
const sparkCtx = sparkline.getContext("2d");

apiKeyInput.value = localStorage.getItem("subway_api_key") || "";

function getHeaders() {
  const key = (localStorage.getItem("subway_api_key") || "").trim();
  return key ? { "x-api-key": key } : {};
}

async function apiFetch(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...getHeaders(),
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

function actionTone(action) {
  if (["JUMP", "SLIDE", "HOVERBOARD"].includes(action)) return "active";
  return "neutral";
}

function setStatusMessage(message, isError = false) {
  formMessage.textContent = message;
  formMessage.className = `status-msg ${isError ? "error" : "ok"}`;
}

function drawSparkline(history) {
  sparkCtx.clearRect(0, 0, sparkline.width, sparkline.height);
  if (!history.length) return;

  const fpsList = history.map((item) => Number(item.fps || 0));
  const maxFps = Math.max(30, ...fpsList);
  const padding = 18;
  const width = sparkline.width - padding * 2;
  const height = sparkline.height - padding * 2;
  const step = width / Math.max(1, fpsList.length - 1);

  sparkCtx.lineWidth = 2;
  sparkCtx.strokeStyle = "#23d39c";
  sparkCtx.beginPath();

  fpsList.forEach((fps, index) => {
    const x = padding + step * index;
    const y = padding + height - (fps / maxFps) * height;
    if (index === 0) sparkCtx.moveTo(x, y);
    else sparkCtx.lineTo(x, y);
  });
  sparkCtx.stroke();

  sparkCtx.strokeStyle = "rgba(157, 188, 201, 0.28)";
  sparkCtx.beginPath();
  sparkCtx.moveTo(padding, padding + height);
  sparkCtx.lineTo(sparkline.width - padding, padding + height);
  sparkCtx.stroke();
}

async function refreshTelemetry() {
  const data = await apiFetch("/v1/telemetry?limit=80");
  const latest = data.latest;
  if (!latest) {
    trackingState.textContent = "No stream";
    return;
  }

  actionBadge.textContent = latest.action;
  actionBadge.className = `badge ${actionTone(latest.action)}`;
  fpsValue.textContent = String(latest.fps);
  trackingState.textContent = latest.has_hand ? "Hand detected" : "No hand";
  activeProfile.textContent = latest.profile;
  lastUpdateText.textContent = `Last update: ${latest.timestamp}`;
  drawSparkline(data.history || []);
}

function renderProfiles(payload) {
  const active = payload.active;
  const items = payload.items || [];
  profilesList.innerHTML = "";
  if (!items.length) {
    profilesList.innerHTML = "<p class='subtle'>No profiles found.</p>";
    return;
  }

  items.forEach((profile) => {
    const card = document.createElement("article");
    card.className = "profile-item";
    card.innerHTML = `
      <h4>${profile.name}${profile.name === active ? " (active)" : ""}</h4>
      <p>${profile.description}</p>
      <p>Bounds ${profile.left_bound} - ${profile.right_bound} | Cooldown ${profile.cooldown_ms}ms</p>
      <button type="button" data-name="${profile.name}">Activate</button>
    `;
    card.querySelector("button").addEventListener("click", async () => {
      try {
        await apiFetch(`/v1/profiles/${profile.name}/activate`, { method: "POST" });
        setStatusMessage(`Profile '${profile.name}' activated.`);
        await refreshProfiles();
      } catch (error) {
        setStatusMessage(error.message, true);
      }
    });
    profilesList.appendChild(card);
  });
}

async function refreshProfiles() {
  const payload = await apiFetch("/v1/profiles");
  renderProfiles(payload);
}

async function submitProfile(event) {
  event.preventDefault();

  const name = document.getElementById("profileName").value.trim();
  const body = {
    description: document.getElementById("profileDescription").value.trim(),
    left_bound: Number(document.getElementById("leftBound").value),
    right_bound: Number(document.getElementById("rightBound").value),
    detection_confidence: Number(document.getElementById("detectionConfidence").value),
    presence_confidence: Number(document.getElementById("presenceConfidence").value),
    tracking_confidence: Number(document.getElementById("trackingConfidence").value),
    cooldown_ms: Number(document.getElementById("cooldownMs").value),
  };

  if (body.left_bound >= body.right_bound) {
    setStatusMessage("left_bound must be lower than right_bound.", true);
    return;
  }

  try {
    await apiFetch(`/v1/profiles/${encodeURIComponent(name)}`, {
      method: "PUT",
      body: JSON.stringify(body),
    });
    setStatusMessage(`Profile '${name}' saved.`);
    await refreshProfiles();
  } catch (error) {
    setStatusMessage(error.message, true);
  }
}

saveApiKeyBtn.addEventListener("click", () => {
  localStorage.setItem("subway_api_key", apiKeyInput.value.trim());
  setStatusMessage("API key saved in browser.");
});

refreshProfilesBtn.addEventListener("click", () => {
  refreshProfiles().catch((error) => setStatusMessage(error.message, true));
});

profileForm.addEventListener("submit", submitProfile);

async function bootstrap() {
  try {
    await refreshProfiles();
    await refreshTelemetry();
    setStatusMessage("Dashboard connected.");
  } catch (error) {
    setStatusMessage(error.message, true);
  }
}

bootstrap();
setInterval(() => {
  refreshTelemetry().catch(() => {
    trackingState.textContent = "Connection lost";
  });
}, 1200);
