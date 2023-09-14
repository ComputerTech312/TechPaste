async function encrypt(data) {
    const key = await window.crypto.subtle.generateKey(
        {
            name: "AES-GCM",
            length: 256,
        },
        true,
        ["encrypt", "decrypt"]
    );

    const iv = window.crypto.getRandomValues(new Uint8Array(12));

    const encryptedContent = await window.crypto.subtle.encrypt(
        {
            name: "AES-GCM",
            iv: iv,
        },
        key,
        new TextEncoder().encode(data)
    );

    const keyExport = await window.crypto.subtle.exportKey(
        "jwk",
        key
    );

    return {
        encryptedContent: new Uint8Array(encryptedContent),
        iv: iv,
        key: keyExport,
    };
}

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
    if(textArea) {
        textArea.addEventListener('input', () => {
            textArea.style.height = 'auto';
            textArea.style.height = textArea.scrollHeight + 'px';
        });
    }
});
