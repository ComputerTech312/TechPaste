/*
 *  client.js: facilitates connection between frontend and RESTful backend
 *             services via AJAX
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

function escapeHtml(unsafe)
{
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

function ajax_submit_paste(c,e) {
    /* content encryption */
    var secret = generate_secret();
    var encrypted_data = encrypt_paste(secret, c);

    /* content submission */
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/v1/secure-paste");
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onload = function() {
        if (xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);

            document.getElementById("paste-form").hidden = true;
            var statusDiv = document.getElementById("paste-status");
            statusDiv.innerHTML = `
                <p>Paste created with ID: ${response.id}</p>
                <p>Paste was encrypted using secret ${secret}</p>
                <p>You can access it <a href="/${response.id}#${secret}">here</a></p>
            `;
            statusDiv.hidden = false;
        } else {
            alert("Error submitting paste. Please check your connection and try again");
        }
    };
    xhr.send(JSON.stringify({"data": encrypted_data, "expiry": e}));
}

function ajax_pull_paste(id, secret) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/api/v1/secure-paste/" + id);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onload = function() {
        if (xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);

            /* content decryption and display */
            var decrypted_content = decrypt_paste(secret, response.data);

            document.getElementById("load-status").hidden = true;
            var content = document.getElementById("content");
            content.hidden = false;
            content.innerHTML = `<pre>${escapeHtml(decrypted_content)}</pre>`
        } else if (xhr.status === 404) {
            document.getElementById("load-status").innerHTML = "Paste not found or has expired. Please try again later.";
        }
    };
    xhr.send();
}

function on_submit_form() {
    console.log("submit button clicked");
    var content = document.getElementById("content-textarea").value;
    var expiry = document.getElementById("expiry-select").value;
    ajax_submit_paste(content, expiry);
}
