// Lightweight auth helper for login.html and register.html
// Adjust API_BASE if your backend runs on a different host/port.
const API_BASE = (window.__API_BASE__ || "http://127.0.0.1:8000");

function saveTokens(accessToken, refreshToken) {
  localStorage.setItem("vex_access_token", accessToken);
  localStorage.setItem("vex_refresh_token", refreshToken);
}

function clearTokens() {
  localStorage.removeItem("vex_access_token");
  localStorage.removeItem("vex_refresh_token");
  localStorage.removeItem("vex_user");
}

function getAuthHeader() {
  const t = localStorage.getItem("vex_access_token");
  return t ? { "Authorization": "Bearer " + t } : {};
}

async function fetchMe() {
  try {
    const res = await fetch(`${API_BASE}/api/me`, {
      method: "GET",
      headers: {
        "Accept": "application/json",
        ...getAuthHeader()
      }
    });
    if (!res.ok) return null;
    const json = await res.json();
    // backend returns { success: True, user: {...} }
    if (json && json.user) {
      localStorage.setItem("vex_user", JSON.stringify(json.user));
      return json.user;
    }
    return null;
  } catch (err) {
    console.error("fetchMe error", err);
    return null;
  }
}

async function loginUser(email, password) {
  try {
    const res = await fetch(`${API_BASE}/api/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) {
      const err = await res.json().catch(()=>({detail:res.statusText}));
      throw new Error(err.detail || "Login failed");
    }
    const { access_token, refresh_token } = await res.json();
    saveTokens(access_token, refresh_token);
    await fetchMe();
    // redirect to dashboard
    window.location.href = "dashboard.html";
  } catch (err) {
    console.error("loginUser error", err);
    alert("Login error: " + err.message);
  }
}

async function registerUser(username, email, password) {
  try {
    const res = await fetch(`${API_BASE}/api/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password })
    });
    if (!res.ok) {
      const err = await res.json().catch(()=>({detail:res.statusText}));
      throw new Error(err.detail || "Registration failed");
    }
    // backend currently returns access_token and refresh_token (auto-login)
    const { access_token, refresh_token } = await res.json();
    saveTokens(access_token, refresh_token);
    await fetchMe();
    window.location.href = "dashboard.html";
  } catch (err) {
    console.error("registerUser error", err);
    alert("Registration error: " + err.message);
  }
}

async function logout() {
  const refreshToken = localStorage.getItem("vex_refresh_token");
  try {
    if (refreshToken) {
      await fetch(`${API_BASE}/api/logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken })
      });
    }
  } catch (err) {
    console.warn("logout request failed (continuing to clear client state)", err);
  } finally {
    clearTokens();
    window.location.href = "login.html";
  }
}

/* Attach to forms if present on the page */
document.addEventListener("DOMContentLoaded", () => {
  // LOGIN
  const loginForm = document.querySelector("#loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const email = document.querySelector("#email").value.trim();
      const password = document.querySelector("#password").value;
      if (!email || !password) {
        alert("Please enter email and password.");
        return;
      }
      loginUser(email, password);
    });
  }

  // REGISTER - note: register.html currently has no id on the form; we look for form on the page
  const registerForm = document.querySelector("#registerForm") || (document.location.pathname.endsWith("register.html") && document.querySelector("form"));
  if (registerForm) {
    registerForm.addEventListener("submit", (e) => {
      e.preventDefault();
      // Try to find inputs; if register.html uses the current structure, query them by type/order
      const usernameInput = registerForm.querySelector('input[type="text"]') || registerForm.querySelector("#username");
      const emailInput = registerForm.querySelector('input[type="email"]') || registerForm.querySelector("#email");
      const passwordInputs = registerForm.querySelectorAll('input[type="password"]');
      const username = usernameInput ? usernameInput.value.trim() : "";
      const email = emailInput ? emailInput.value.trim() : "";
      const password = passwordInputs.length ? passwordInputs[0].value : "";
      const confirm = passwordInputs.length > 1 ? passwordInputs[1].value : null;

      if (!username || !email || !password) {
        alert("Please fill all required fields.");
        return;
      }
      if (confirm !== null && password !== confirm) {
        alert("Passwords do not match.");
        return;
      }
      if (password.length < 8) {
        alert("Password must be at least 8 characters.");
        return;
      }
      registerUser(username, email, password);
    });
  }

  // LOGOUT - attach to any element with data-logout or class .btn-logout
  document.querySelectorAll("[data-logout], .btn-logout").forEach(el => {
    el.addEventListener("click", (e) => {
      e.preventDefault();
      logout();
    });
  });
});