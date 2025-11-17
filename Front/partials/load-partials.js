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

  function setActiveNav() {
    const path = location.pathname.split('/').pop().toLowerCase();
    const links = document.querySelectorAll('#site-header nav a');
    links.forEach(a => {
      const href = (a.getAttribute('href') || '').split('/').pop().toLowerCase();
      a.classList.remove('active');
      if (!href) return;
      // treat Index.html and index.html and empty path as home
      if ((href === 'index.html' && (path === '' || path === 'index.html' || path === 'Index.html')) || href === path) {
        a.classList.add('active');
      }
    });
  }

  document.addEventListener('DOMContentLoaded', function() {
    loadPartial('partials/header.html', '#site-header');
    loadPartial('partials/footer.html', '#site-footer');
  });
})();
