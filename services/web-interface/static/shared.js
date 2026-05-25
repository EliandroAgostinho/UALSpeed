// ─────────────────────────────────────────
// TEMA CLARO/ESCURO
// ─────────────────────────────────────────
function iniciarTema() {
    const temaGuardado = localStorage.getItem('tema') || 'escuro';
    aplicarTema(temaGuardado);
}

function aplicarTema(tema) {
    document.documentElement.setAttribute('data-tema', tema);
    localStorage.setItem('tema', tema);
    const btn = document.getElementById('btn-tema');
    if (btn) {
        btn.textContent = tema === 'escuro' ? '☀️ Tema Claro' : '🌙 Tema Escuro';
    }
}

function toggleTema() {
    const temaActual = localStorage.getItem('tema') || 'escuro';
    aplicarTema(temaActual === 'escuro' ? 'claro' : 'escuro');
}

// ─────────────────────────────────────────
// NAVEGAÇÃO — marca a página actual
// ─────────────────────────────────────────
function iniciarNavegacao() {
    const pagina = window.location.pathname;
    const links = document.querySelectorAll('nav a');

    links.forEach(link => {
        const href = link.getAttribute('href');
        // Verifica se o link corresponde à página actual
        const activo = (href === '/' && pagina === '/') ||
                       (href !== '/' && pagina.startsWith(href));
        if (activo) {
            link.classList.add('nav-activo');
        }
    });
}

// Corre quando a página carrega
document.addEventListener('DOMContentLoaded', () => {
    iniciarTema();
    iniciarNavegacao();
});