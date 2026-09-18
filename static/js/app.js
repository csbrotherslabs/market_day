const body = document.body;
const toggle = document.getElementById('themeToggle');
const collapseBtn = document.getElementById('collapseBtn');
const appShell = document.getElementById('appShell');
const profileMenuToggle = document.getElementById('profileMenuToggle');
const profileMenu = document.getElementById('profileMenu');
const profileMenuClose = document.getElementById('profileMenuClose');
const accountDrawerBackdrop = document.getElementById('accountDrawerBackdrop');
const mobileSidebar = document.getElementById('mobileSidebar');
const mobileSidebarClose = document.getElementById('mobileSidebarClose');
const mobileSidebarBackdrop = document.getElementById('mobileSidebarBackdrop');

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

const closeMobileSidebar = () => {
  if (!mobileSidebar) return;
  mobileSidebar.classList.remove('mobile-open');
  body.classList.remove('mobile-sidebar-open');
  collapseBtn?.setAttribute('aria-expanded', 'false');
  if (mobileSidebarBackdrop) {
    mobileSidebarBackdrop.classList.add('hidden');
    mobileSidebarBackdrop.setAttribute('aria-hidden', 'true');
  }
};

const openMobileSidebar = () => {
  if (!mobileSidebar) return;
  mobileSidebar.classList.add('mobile-open');
  body.classList.add('mobile-sidebar-open');
  collapseBtn?.setAttribute('aria-expanded', 'true');
  if (mobileSidebarBackdrop) {
    mobileSidebarBackdrop.classList.remove('hidden');
    mobileSidebarBackdrop.setAttribute('aria-hidden', 'false');
  }
};

if (collapseBtn && appShell) {
  collapseBtn.setAttribute('aria-expanded', 'false');
  collapseBtn.addEventListener('click', () => {
    if (window.innerWidth <= 900) {
      mobileSidebar?.classList.contains('mobile-open') ? closeMobileSidebar() : openMobileSidebar();
      return;
    }
    appShell.classList.toggle('collapsed');
    localStorage.setItem('marketflow-sidebar', appShell.classList.contains('collapsed') ? 'collapsed' : 'expanded');
  });
}
mobileSidebarClose?.addEventListener('click', closeMobileSidebar);
mobileSidebarBackdrop?.addEventListener('click', closeMobileSidebar);
mobileSidebar?.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMobileSidebar));

window.addEventListener('resize', () => {
  if (!appShell) return;
  if (window.innerWidth <= 900) {
    appShell.classList.remove('collapsed');
    closeMobileSidebar();
  } else if (localStorage.getItem('marketflow-sidebar') === 'collapsed') {
    appShell.classList.add('collapsed');
  }
});

if (profileMenuToggle && profileMenu) {
  const isMobileAccountMenu = () => window.innerWidth <= 700;

  const openProfileMenu = () => {
    profileMenu.classList.remove('hidden');
    profileMenuToggle.setAttribute('aria-expanded', 'true');
    if (isMobileAccountMenu()) {
      body.classList.add('account-drawer-open');
      if (accountDrawerBackdrop) {
        accountDrawerBackdrop.classList.remove('hidden');
        accountDrawerBackdrop.setAttribute('aria-hidden', 'false');
      }
    }
  };

  const closeProfileMenu = () => {
    profileMenu.classList.add('hidden');
    profileMenuToggle.setAttribute('aria-expanded', 'false');
    body.classList.remove('account-drawer-open');
    if (accountDrawerBackdrop) {
      accountDrawerBackdrop.classList.add('hidden');
      accountDrawerBackdrop.setAttribute('aria-hidden', 'true');
    }
  };

  profileMenuToggle.addEventListener('click', (event) => {
    event.stopPropagation();
    if (profileMenu.classList.contains('hidden')) {
      openProfileMenu();
    } else {
      closeProfileMenu();
    }
  });

  if (profileMenuClose) profileMenuClose.addEventListener('click', closeProfileMenu);
  if (accountDrawerBackdrop) accountDrawerBackdrop.addEventListener('click', closeProfileMenu);

  document.addEventListener('click', (event) => {
    if (!isMobileAccountMenu() && !profileMenu.contains(event.target) && !profileMenuToggle.contains(event.target)) {
      closeProfileMenu();
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !profileMenu.classList.contains('hidden')) closeProfileMenu();
    if (event.key === 'Escape') closeMobileSidebar();
  });

  window.addEventListener('resize', () => {
    if (!profileMenu.classList.contains('hidden')) closeProfileMenu();
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


// Add marketplace products to the session cart without reloading the page.
document.addEventListener('submit', async (event) => {
  const form = event.target.closest('.md-cart-form');
  if (!form) return;
  event.preventDefault();

  const button = form.querySelector('.md-cart-button');
  if (!button || button.disabled) return;
  const original = button.innerHTML;
  button.disabled = true;
  button.classList.add('is-adding');
  button.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i><span>Adding...</span>';

  try {
    const response = await fetch(form.action, {
      method: 'POST',
      body: new FormData(form),
      headers: {'X-Requested-With': 'XMLHttpRequest'},
      credentials: 'same-origin'
    });
    if (!response.ok) throw new Error('Unable to add product');
    const data = await response.json();

    const count = document.getElementById('navbarCartCount');
    if (count) {
      count.textContent = data.cart_count;
      count.classList.remove('hidden');
      count.classList.remove('cart-count-pop');
      void count.offsetWidth;
      count.classList.add('cart-count-pop');
    }

    button.classList.remove('is-adding');
    button.classList.add('is-added');
    button.innerHTML = '<i class="fa-solid fa-check"></i><span>Added to cart</span>';
    window.setTimeout(() => {
      button.classList.remove('is-added');
      button.innerHTML = original;
      button.disabled = false;
    }, 1300);
  } catch (error) {
    button.classList.remove('is-adding');
    button.classList.add('is-error');
    button.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i><span>Try again</span>';
    window.setTimeout(() => {
      button.classList.remove('is-error');
      button.innerHTML = original;
      button.disabled = false;
    }, 1600);
  }
});
