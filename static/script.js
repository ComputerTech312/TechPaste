function toggleTheme() {
    const toggled = document.body.classList.toggle('dark-mode');
    localStorage.setItem('dark-mode', toggled);
    document.getElementById('theme-toggle-input').checked = toggled;
}

document.addEventListener('DOMContentLoaded', (event) => {
    const darkMode = localStorage.getItem('dark-mode') === 'true';
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
