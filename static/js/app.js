const body = document.body;
const toggle = document.getElementById('themeToggle');
const collapseBtn = document.getElementById('collapseBtn');
const appShell = document.getElementById('appShell');

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
