function toggleTheme() {
    const toggled = document.body.classList.toggle('dark-mode');
    localStorage.setItem('dark-mode', toggled);
    document.getElementById('theme-toggle-input').checked = toggled;
}

document.addEventListener('DOMContentLoaded', (event) => {
    const prefersDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    const darkMode = localStorage.getItem('dark-mode') === 'true' || prefersDarkMode;
    document.body.classList.toggle('dark-mode', darkMode);
    document.getElementById('theme-toggle-input').checked = darkMode;

    const textArea = document.querySelector('textarea');
    if (textArea) {
        textArea.addEventListener('input', () => {
            textArea.style.height = 'auto';
            textArea.style.height = textArea.scrollHeight + 'px';
        });
    }
});