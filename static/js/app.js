const body = document.body;
const toggle = document.getElementById('themeToggle');
const collapseBtn = document.getElementById('collapseBtn');
const appShell = document.getElementById('appShell');
const profileMenuToggle = document.getElementById('profileMenuToggle');
const profileMenu = document.getElementById('profileMenu');

const savedTheme = localStorage.getItem('marketflow-theme');
const savedSidebar = localStorage.getItem('marketflow-sidebar');

if (savedTheme === 'light') {
  body.classList.add('light');
}

if (savedSidebar === 'collapsed' && window.innerWidth > 900 && appShell) {
  appShell.classList.add('collapsed');
}

if (toggle) {
  toggle.addEventListener('click', () => {
    body.classList.toggle('light');
    localStorage.setItem('marketflow-theme', body.classList.contains('light') ? 'light' : 'dark');
  });
}

if (collapseBtn && appShell) {
  collapseBtn.addEventListener('click', () => {
    if (window.innerWidth <= 900) return;
    appShell.classList.toggle('collapsed');
    localStorage.setItem('marketflow-sidebar', appShell.classList.contains('collapsed') ? 'collapsed' : 'expanded');
  });
}

window.addEventListener('resize', () => {
  if (!appShell) return;
  if (window.innerWidth <= 900) {
    appShell.classList.remove('collapsed');
  } else if (localStorage.getItem('marketflow-sidebar') === 'collapsed') {
    appShell.classList.add('collapsed');
  }
});

if (profileMenuToggle && profileMenu) {
  profileMenuToggle.addEventListener('click', () => {
    const willOpen = profileMenu.classList.contains('hidden');
    profileMenu.classList.toggle('hidden');
    profileMenuToggle.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
  });

  document.addEventListener('click', (event) => {
    if (!profileMenu.contains(event.target) && !profileMenuToggle.contains(event.target)) {
      profileMenu.classList.add('hidden');
      profileMenuToggle.setAttribute('aria-expanded', 'false');
    }
  });
}

// Add a non-destructive full-template preview action to the store creation cards.
if (window.location.pathname.endsWith('/sellers/stores/add/')) {
  if (!document.getElementById('templateCardActionStyles')) {
    const style = document.createElement('style');
    style.id = 'templateCardActionStyles';
    style.textContent = `
      .template-grid {
        grid-template-columns: repeat(auto-fit, minmax(285px, 1fr)) !important;
        align-items: stretch;
      }
      .template-card {
        height: 100%;
        min-width: 0;
      }
      .template-title-row {
        align-items: flex-start;
      }
      .template-title-row h3 {
        min-width: 0;
      }
      .template-badge {
        flex: 0 0 auto;
      }
      .template-card-actions {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 8px;
        width: 100%;
        margin-top: auto;
        padding-top: 4px;
        align-items: stretch;
      }
      .template-card-actions.is-narrow {
        grid-template-columns: 1fr;
      }
      .template-card-actions .btn {
        width: 100% !important;
        min-width: 0;
        min-height: 36px;
        height: 36px;
        margin: 0 !important;
        padding: 7px 9px;
        font-size: 11.5px;
        line-height: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .template-card-actions.is-narrow .btn {
        height: 38px;
        white-space: normal;
        overflow: visible;
        text-overflow: clip;
      }
      @media (max-width: 980px) {
        .template-grid {
          grid-template-columns: repeat(2, minmax(260px, 1fr)) !important;
        }
      }
      @media (max-width: 640px) {
        .template-grid {
          grid-template-columns: 1fr !important;
        }
      }
    `;
    document.head.appendChild(style);
  }

  document.querySelectorAll('.template-card').forEach((card) => {
    const selectLink = card.querySelector('a[href^="?template="]');
    if (!selectLink || card.querySelector('.template-preview-action')) return;

    const match = selectLink.getAttribute('href').match(/\?template=([^&]+)/);
    if (!match) return;

    const templateKey = encodeURIComponent(match[1]);
    const actions = document.createElement('div');
    actions.className = 'template-card-actions';

    const previewLink = document.createElement('a');
    previewLink.className = 'btn btn-outline btn-sm template-preview-action';
    previewLink.href = `/sellers/stores/templates/${templateKey}/preview/`;
    previewLink.target = '_blank';
    previewLink.rel = 'noopener';
    previewLink.textContent = 'Preview Template';

    selectLink.classList.add('btn-sm');
    actions.appendChild(previewLink);
    actions.appendChild(selectLink);
    card.appendChild(actions);

    const syncCardActions = () => {
      actions.classList.toggle('is-narrow', card.getBoundingClientRect().width < 350);
    };

    syncCardActions();

    if ('ResizeObserver' in window) {
      const observer = new ResizeObserver(syncCardActions);
      observer.observe(card);
    } else {
      window.addEventListener('resize', syncCardActions);
    }
  });
}
