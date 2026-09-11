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

// Store-template selector enhancements: responsive actions + dedicated AI image slots.
if (window.location.pathname.endsWith('/sellers/stores/add/')) {
  const templateImages = {
    fresh_simple: {
      file: '/static/images/store_templates/fresh-simple-hero.webp',
      label: 'Fresh & Simple template image',
      placeholder: 'Fresh produce market hero'
    },
    boutique: {
      file: '/static/images/store_templates/boutique-hero.webp',
      label: 'Boutique template image',
      placeholder: 'African spices and specialty foods'
    },
    story_impact: {
      file: '/static/images/store_templates/story-impact-hero.webp',
      label: 'Story & Impact template image',
      placeholder: 'Local harvest and community story'
    },
    modern_market: {
      file: '/static/images/store_templates/modern-market-hero.webp',
      label: 'Modern Market template image',
      placeholder: 'Modern Ghana market seller'
    },
    premium_showcase: {
      file: '/static/images/store_templates/premium-showcase-hero.webp',
      label: 'Premium Showcase template image',
      placeholder: 'Premium produce harvest still life'
    },
    creative_unique: {
      file: '/static/images/store_templates/creative-unique-hero.webp',
      label: 'Creative & Unique template image',
      placeholder: 'Market sellers and community collage'
    }
  };

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
      .template-preview {
        height: 205px !important;
        padding: 0 !important;
        position: relative;
        isolation: isolate;
        background: #eaf3e8 !important;
      }
      .template-preview .preview-nav,
      .template-preview .preview-hero,
      .template-preview .preview-products {
        display: none !important;
      }
      .template-image-slot {
        position: absolute;
        inset: 0;
        overflow: hidden;
        background: linear-gradient(135deg, #e8f4e5, #d6ead1);
      }
      .template-image-slot img {
        width: 100%;
        height: 100%;
        display: block;
        object-fit: cover;
        object-position: center;
      }
      .template-image-slot.is-empty img {
        display: none;
      }
      .template-image-placeholder {
        position: absolute;
        inset: 0;
        display: none;
        align-items: center;
        justify-content: center;
        padding: 24px;
        text-align: center;
        color: #55705b;
        background:
          radial-gradient(circle at 25% 25%, rgba(255,255,255,.8), transparent 30%),
          linear-gradient(135deg, #edf7ea, #d8ead3);
      }
      .template-image-slot.is-empty .template-image-placeholder {
        display: flex;
      }
      .template-image-placeholder-inner {
        max-width: 210px;
      }
      .template-image-placeholder-icon {
        width: 42px;
        height: 42px;
        margin: 0 auto 10px;
        border-radius: 13px;
        display: grid;
        place-items: center;
        background: rgba(15,159,82,.12);
        color: #0b8f48;
        font-size: 20px;
      }
      .template-image-placeholder strong {
        display: block;
        color: #183c24;
        font-size: 13px;
        margin-bottom: 5px;
      }
      .template-image-placeholder small {
        display: block;
        font-size: 10.5px;
        line-height: 1.45;
        opacity: .75;
      }
      .template-image-overlay {
        position: absolute;
        inset: auto 0 0;
        min-height: 62px;
        padding: 22px 14px 11px;
        display: flex;
        align-items: flex-end;
        background: linear-gradient(to top, rgba(4,20,10,.72), transparent);
        color: #fff;
        pointer-events: none;
      }
      .template-image-overlay span {
        font-size: 10px;
        font-weight: 650;
        letter-spacing: .02em;
        opacity: .92;
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
        .template-preview {
          height: 220px !important;
        }
      }
    `;
    document.head.appendChild(style);
  }

  document.querySelectorAll('.template-card').forEach((card) => {
    const selectLink = card.querySelector('a[href^="?template="]');
    if (!selectLink) return;

    const match = selectLink.getAttribute('href').match(/\?template=([^&]+)/);
    if (!match) return;

    const rawTemplateKey = match[1];
    const templateKey = encodeURIComponent(rawTemplateKey);
    const imageConfig = templateImages[rawTemplateKey];
    const preview = card.querySelector('.template-preview');

    if (preview && imageConfig && !preview.querySelector('.template-image-slot')) {
      const slot = document.createElement('div');
      slot.className = 'template-image-slot';

      const image = document.createElement('img');
      image.src = imageConfig.file;
      image.alt = imageConfig.label;
      image.loading = 'lazy';
      image.decoding = 'async';

      const placeholder = document.createElement('div');
      placeholder.className = 'template-image-placeholder';
      placeholder.innerHTML = `
        <div class="template-image-placeholder-inner">
          <div class="template-image-placeholder-icon">▧</div>
          <strong>AI image slot</strong>
          <small>${imageConfig.placeholder}<br>${imageConfig.file.split('/').pop()}</small>
        </div>
      `;

      const overlay = document.createElement('div');
      overlay.className = 'template-image-overlay';
      overlay.innerHTML = `<span>${imageConfig.file.split('/').pop()}</span>`;

      image.addEventListener('error', () => slot.classList.add('is-empty'));
      image.addEventListener('load', () => slot.classList.remove('is-empty'));

      slot.appendChild(image);
      slot.appendChild(placeholder);
      slot.appendChild(overlay);
      preview.appendChild(slot);
    }

    if (!card.querySelector('.template-preview-action')) {
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
    }

    const actions = card.querySelector('.template-card-actions');
    if (!actions) return;

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
