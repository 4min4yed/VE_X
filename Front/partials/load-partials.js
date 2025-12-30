(function() {
  async function loadPartial(url, selector) {
    try {
      const resp = await fetch(url);
      if (!resp.ok) return;
      const html = await resp.text();
      const container = document.querySelector(selector);
      if (container) container.innerHTML = html;
      setActiveNav();
    } catch (e) {
      // silently fail
      console.error('Failed to load partial:', url, e);
    }
  }

  // --- Auth helpers (populate auth area across pages) ---
  const API_BASE = window.__API_BASE__ || "http://127.0.0.1:8000";

  async function apiFetch(path, options = {}){
    return fetch(API_BASE + path, options);
  }

  async function tryRefresh(refreshToken){
    if(!refreshToken) return false;
    try{
      const r = await fetch(`${API_BASE}/api/refresh`, {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({refresh_token: refreshToken})
      });
      if(!r.ok) return false;
      const j = await r.json();
      if(j.access_token && j.refresh_token){
        localStorage.setItem('vex_access_token', j.access_token);
        localStorage.setItem('vex_refresh_token', j.refresh_token);
        return true;
      }
    }catch(e){ console.warn('refresh failed', e); }
    return false;
  }

  function renderAuthArea(user){
    const auth = document.getElementById('auth-area');
    if(!auth) return;
    if(user){
      auth.innerHTML = `
        <span class="nav-user">${user.username || user.email}</span>
        <button id="btn-logout" class="btn-logout">Sign out</button>
      `;
      const btn = document.getElementById('btn-logout');
      if(btn) btn.addEventListener('click', (e)=>{ e.preventDefault(); if(window.logout) window.logout(); else location.href='login.html'; });
    } else {
      auth.innerHTML = `<a href="login.html" class="btn-login">Login</a>`;
    }
  }

  async function populateAuth(){
    const authArea = document.getElementById('auth-area');
    if(!authArea) return;
    let userRaw = localStorage.getItem('vex_user');
    let user = userRaw ? JSON.parse(userRaw) : null;
    const access = localStorage.getItem('vex_access_token');
    const refreshToken = localStorage.getItem('vex_refresh_token');

    if(user){ renderAuthArea(user); return; }

    if(!access && refreshToken){
      const ok = await tryRefresh(refreshToken);
      if(!ok){ renderAuthArea(null); return; }
    }

    const curAccess = localStorage.getItem('vex_access_token');
    if(!curAccess) { renderAuthArea(null); return; }

    try{
      const r = await apiFetch('/api/me', {method:'GET', headers: { 'Accept':'application/json', 'Authorization': 'Bearer ' + curAccess }});
      if(r.ok){
        const j = await r.json();
        if(j && j.user){ localStorage.setItem('vex_user', JSON.stringify(j.user)); renderAuthArea(j.user); return; }
      } else if(r.status === 401 && refreshToken){
        const did = await tryRefresh(refreshToken);
        if(did){
          const newAccess = localStorage.getItem('vex_access_token');
          const r2 = await apiFetch('/api/me', {method:'GET', headers: { 'Accept':'application/json', 'Authorization': 'Bearer ' + newAccess }});
          if(r2.ok){ const j2 = await r2.json(); if(j2 && j2.user){ localStorage.setItem('vex_user', JSON.stringify(j2.user)); renderAuthArea(j2.user); return; } }
        }
      }
    }catch(e){ console.warn('populateAuth error', e); }

    renderAuthArea(null);
  }

  function setActiveNav() {
    // Get current page filename
    const path = location.pathname.split('/').pop().toLowerCase();
    const navLinks = {
      'index.html': document.getElementById('nav-home'),
      'analyze.html': document.getElementById('nav-analyze'),
      'dashboard.html': document.getElementById('nav-dashboard'),
      'history.html': document.getElementById('nav-history'),
      'contact.html': document.getElementById('nav-contact')
    };
    
    // Treat Index.html the same as index.html for matching
    const currentPage = (path === 'index.html' || path === '' || path === 'Index.html') ? 'index.html' : path;
    
    // Remove active from all
    Object.values(navLinks).forEach(link => {
      if (link) link.classList.remove('active');
    });
    
    // Add active to current page
    if (navLinks[currentPage]) {
      navLinks[currentPage].classList.add('active');
    }
  }

  document.addEventListener('DOMContentLoaded', function() {
    (async function(){
      await loadPartial('partials/header.html', '#site-header');
      await loadPartial('partials/footer.html', '#site-footer');
      await populateAuth();
    })();
  });
})();
