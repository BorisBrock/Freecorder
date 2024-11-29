const gVersion = "0.2.0"

// Sets the version number in the UI
function setVersion() {
    document.getElementById('version-number').textContent = `Version ${gVersion}`;
}