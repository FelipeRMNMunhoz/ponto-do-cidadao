// =======================
// 📱 MENU MOBILE
// =======================
const botaoMenu = document.getElementById('botaoMenu');
const menuMobile = document.getElementById('menuMobile');
const botaoFecharMenu = document.getElementById('botaoFecharMenu');

function abrirMenu() {
  menuMobile.hidden = false;
  botaoMenu.setAttribute('aria-expanded', 'true');
  document.body.style.overflow = 'hidden';
}

function fecharMenu() {
  menuMobile.hidden = true;
  botaoMenu.setAttribute('aria-expanded', 'false');
  document.body.style.overflow = '';
}

botaoMenu.addEventListener('click', () => {
  menuMobile.hidden ? abrirMenu() : fecharMenu();
});

botaoFecharMenu.addEventListener('click', fecharMenu);

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && !menuMobile.hidden) fecharMenu();
});

// =======================

// Preserve the original logout icon while sending a CSRF-protected POST.
document.querySelectorAll('[data-logout]').forEach(link => {
  link.addEventListener('click', event => {
    event.preventDefault();
    document.getElementById('logout-form').requestSubmit();
  });
});
