// This base URL is used as the destination for REST query calls
var gBaseUrl = "";

// Called when index.html has finished loading
window.addEventListener('DOMContentLoaded', event => {
    setVersion();
    gBaseUrl = document.baseURI;
    console.log("Setting base URI to " + gBaseUrl);
    updateFileList();
});

// When called, requests a new file list from the server and updates the view
function updateFileList() {
    console.log("Updating file list...");
    fetchJSON("api/files").then(jsonData => {
        // Modify the data
        const processedData = jsonData.files.
            filter(file => file.name != "current.mp4").
            map(file => {
                const timeStrings = parseTimeString(file.name);
                return {
                    filename: file.name,
                    baseurl: gBaseUrl,
                    size: `${Math.round(file.size / 1024 / 1024)} MB`,
                    startdate: timeStrings[0],
                    starttime: timeStrings[1],
                    enddate: timeStrings[2],
                    endtime: timeStrings[3],
                };
            });

        // Show the data
        const templateSource = document.getElementById('row-template').innerHTML;
        const template = Handlebars.compile(templateSource);
        const html = template({ files: processedData });
        document.getElementById('table-body').innerHTML = html;
    });
}

// Async function to get JSON data from the server
async function fetchJSON(uri) {
    const response = await fetch(gBaseUrl + uri);
    const data = await response.json();
    return data;
}

function parseTimeString(s) {
    s = s.replace(".mp4", "")
    const parts = s.split("_");
    var dateFrom = parts[1];
    var timeFrom = parts[2].replaceAll("-", ":");
    var dateTo = parts[3];
    var timeTo = parts[4].replaceAll("-", ":");
    return [dateFrom, timeFrom, dateTo, timeTo];
}

function playVideo(fileName) {
    const modal = document.getElementById('video-modal');
    const videoPlayer = document.getElementById('video-player');
    videoPlayer.src = gBaseUrl + "video/" + fileName; // Set the video source
    modal.style.display = 'flex'; // Show the modal
}

function stopVideo() {
    const modal = document.getElementById('video-modal');
    const videoPlayer = document.getElementById('video-player');
    videoPlayer.pause(); // Pause the video when closing
    modal.style.display = 'none'; // Hide the modal
}