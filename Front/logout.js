(function () {
  // Adjust the API base if your backend runs on a different host/port
  const API_BASE = window.__API_BASE__ || "http://127.0.0.1:8000";

  function clearClientAuth() {
    localStorage.removeItem("vex_access_token");
    localStorage.removeItem("vex_refresh_token");
    localStorage.removeItem("vex_user");
  }

  async function callLogoutEndpoint(refreshToken) {
    // Backend expects JSON: { "refresh_token": "<token>" }
    // If you switch to HttpOnly cookies for refresh tokens, send no body and the server will read the cookie.
    try {
      const res = await fetch(`${API_BASE}/api/logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      // It's fine if logout returns non-200 (treat as best-effort)
      return res;
    } catch (err) {
      console.warn("Logout request failed:", err);
      return null;
    }
  }

  async function handleSignOut(e) {
    if (e) e.preventDefault();
    const refreshToken = localStorage.getItem("vex_refresh_token");
    await callLogoutEndpoint(refreshToken);
    clearClientAuth();
    // Redirect to login (or wherever you want)
    window.location.href = "login.html";
  }

  // Attach to #btn-logout and any element with data-logout attribute
  document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("btn-logout");
    if (btn) btn.addEventListener("click", handleSignOut);

    document.querySelectorAll("[data-logout]").forEach((el) => {
      el.addEventListener("click", handleSignOut);
    });
  });

})();