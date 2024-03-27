function encrypt_paste(k,c) {
    return btoa(CryptoJS.AES.encrypt(c, k));
}

function decrypt_paste(k,c) {
    return CryptoJS.AES.decrypt(atob(c), k).toString(CryptoJS.enc.Utf8);
}

function generate_secret() {
    return CryptoJS.lib.WordArray.random(16).toString();;
}