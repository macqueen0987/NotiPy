function toggleLangPopup() {
    const popup = document.getElementById('lang-popup');
    if (!popup) return;
    popup.style.display = popup.style.display === 'block' ? 'none' : 'block';
}

function switchLang(lang) {
    let path = window.location.pathname;
    if (path.includes('/en/')) {
        path = path.replace('/en/', '/' + lang + '/');
    } else if (path.includes('/ko/')) {
        path = path.replace('/ko/', '/' + lang + '/');
    }
    window.location.pathname = path;
}

document.addEventListener('click', function(event) {
    const popup = document.getElementById('lang-popup');
    const btn = document.getElementById('lang-btn');
    if (!popup || !btn) return;
    if (!popup.contains(event.target) && event.target !== btn) {
        popup.style.display = 'none';
    }
});
