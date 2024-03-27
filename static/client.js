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
        } else if (xhr.status === 400) {
            var response = JSON.parse(xhr.responseText);
            if (response.error === "Paste too large") {
                alert("Error: Paste is too large. Please reduce the size and try again.");
            } else {
                alert("Error submitting paste. Please check your connection and try again");
            }
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

            // Split the decrypted content into lines and wrap each line in a <div> tag
            var lines = decrypted_content.split('\n');
            var formatted = lines.map(function(line) {
                return '<div>' + escapeHtml(line) + '</div>';
            }).join('');

            document.getElementById("load-status").hidden = true;
            var content = document.getElementById("content");
            content.hidden = false;
            content.innerHTML = formatted; // Set the innerHTML to the formatted content
        } else if (xhr.status === 404) {
            document.getElementById("load-status").innerHTML = "Paste not found or has expired. Please try again later.";
        }
    };
    xhr.send();
}

function on_submit_form() {
    var content = document.getElementById("content-textarea").value;
    var expiry = document.getElementById("expiry-select").value;
    ajax_submit_paste(content, expiry);
}
