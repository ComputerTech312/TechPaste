document.addEventListener("DOMContentLoaded", (event) => {
    var key = window.location.hash.split("#")[1];
    console.log(key);
    if (!key) {
      document.getElementById("load-status").innerHTML = "No secret was supplied. No content will be displayed at this time.";
      return;
    }
    var parts = window.location.href.split("/");
    var paste_id = parts[parts.length-1].split("#")[0];
    ajax_pull_paste(paste_id, key);
  });