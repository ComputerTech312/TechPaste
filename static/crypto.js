/*
 *  crypto.js: contains cryptographic functions for content encryption
 *
 *  Copyright (C) 2023 David Schultz <me@zpld.me>
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307
 *  USA
 */

function encrypt_paste(k,c) {
    return btoa(CryptoJS.AES.encrypt(c, k));
}

function decrypt_paste(k,c) {
    return CryptoJS.AES.decrypt(atob(c), k).toString(CryptoJS.enc.Utf8);
}

function generate_secret() {
    return CryptoJS.lib.WordArray.random(16).toString();;
}