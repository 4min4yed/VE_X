// Dashboard auth + rendering helper (event-delegation, robust /api/me handling)
const API_BASE = (window.__API_BASE__ || "http://127.0.0.1:8000");

function getAccessToken() {
  return localStorage.getItem("vex_access_token");
}
function getRefreshToken() {
  return localStorage.getItem("vex_refresh_token");
}
function clearClientAuth() {
  localStorage.removeItem("vex_access_token");
  localStorage.removeItem("vex_refresh_token");
  localStorage.removeItem("vex_user");
}

async function callLogoutEndpoint(refreshToken) {
  try {
    const res = await fetch(`${API_BASE}/api/logout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    return res;
  } catch (err) {
    console.warn("Logout request failed:", err);
    return null;
  }
}

async function handleLogout(e) {
  if (e) e.preventDefault();
  // disable further clicks quickly
  try {
    document.body.style.pointerEvents = "none";
    const refreshToken = getRefreshToken();
    await callLogoutEndpoint(refreshToken);
  } finally {
    clearClientAuth();
    window.location.href = "login.html";
  }
}

async function apiGet(path) {
  const token = getAccessToken();
  const headers = token ? { "Authorization": "Bearer " + token } : {};
  const res = await fetch(API_BASE + path, { method: "GET", headers });
  if (res.status === 401) {
    // Not authorized — clear and redirect
    clearClientAuth();
    window.location.href = "login.html";
    return null;
  }
  if (!res.ok) throw new Error(`HTTP ${res.status} ${res.statusText}`);
  return res.json();
}

function setTextIfExists(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

/* Render user into designated elements */
function renderUser(user) {
  if (!user) return;
  const displayName = user.username || user.email || `User ${user.id}`;
  setTextIfExists("user-name", displayName);
  setTextIfExists("user-name-inline", displayName);
  setTextIfExists("user-email", user.email || "");
  setTextIfExists("user-email-inline", user.email || "");
  localStorage.setItem("vex_user", JSON.stringify(user));
}

/* Render stats placeholders */
function renderStats(stats = {}) {
  const { total_scans = 0, safe = 0, suspicious = 0, malicious = 0 } = stats;
  setTextIfExists("total-scans", total_scans);
  setTextIfExists("safe-count", safe);
  setTextIfExists("suspicious-count", suspicious);
  setTextIfExists("malicious-count", malicious);
}

/* Event delegation for logout (works even if DOM is replaced later) */
document.addEventListener("click", function (ev) {
  const btn = ev.target.closest && (ev.target.closest("#btn-logout") || ev.target.closest("[data-logout]") || ev.target.closest(".btn-logout"));
  if (btn) {
    handleLogout(ev);
  }
});

document.addEventListener("DOMContentLoaded", async () => {
  // Quick guard: if no token, redirect to login
  if (!getAccessToken()) {
    window.location.href = "login.html";
    return;
  }

  // Try to get user from localStorage to show something immediately
  let user = null;
  try {
    const stored = localStorage.getItem("vex_user");
    if (stored) user = JSON.parse(stored);
    if (user) renderUser(user);
  } catch (e) {
    console.debug("No stored user");
  }

  // Fetch canonical /api/me to validate token and get username
  try {
    const meJson = await apiGet("/api/me");
    if (meJson && meJson.user) {
      user = meJson.user;
      renderUser(user);
    } else {
      console.warn("/api/me returned unexpected response:", meJson);
      clearClientAuth();
      window.location.href = "login.html";
      return;
    }
  } catch (err) {
    console.error("Failed to fetch /api/me:", err);
    return;
  }

  // Fetch per-user stats if available
  try {
    const statsJson = await apiGet(`/api/user/${user.id}/stats`);
    if (statsJson) {
      if (statsJson.stats) renderStats(statsJson.stats);
      else renderStats(statsJson);
    }
  } catch (err) {
    console.debug("User stats not available or failed:", err);
  }

  // Fetch history if available and render
  try {
    const histJson = await apiGet(`/api/user/${user.id}/history`);
    if (histJson && Array.isArray(histJson.history)) {
      const container = document.getElementById("recent-history");
      if (container) {
        container.innerHTML = "";
        histJson.history.slice(0, 10).forEach(item => {
          const row = document.createElement("div");
          row.className = "history-item";
          row.innerHTML = `
            <div class="icon"><i class="fas fa-file"></i></div>
            <div class="file-info">
              <h4>${item.filename}</h4>
              <p>${item.date} • ${item.size} • ${item.threats || 0} threats</p>
            </div>
            <span class="badge ${item.status || 'safe'}">${(item.status || 'Safe').toString()}</span>
            <button class="view-btn"><i class="fas fa-chevron-right"></i></button>
          `;
          container.appendChild(row);
        });
      }
    }
  } catch (err) {
    console.debug("User history not available or failed:", err);
  }
});