// This file contains the JavaScript code for the web application. 
// It handles user interactions, makes AJAX requests to the Flask backend, 
// and updates the UI based on the responses.

document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('#convert-form');
    const resultDiv = document.querySelector('#result');

    form.addEventListener('submit', async function (event) {
        event.preventDefault(); // Prevent the default form submission

        // Clear previous results
        resultDiv.innerHTML = '';

        // Prepare form data
        const formData = new FormData(form);

        try {
            // Send the form data to the server
            const response = await fetch('/convert', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.status === 'success') {
                // Display the download button
                const downloadLink = document.createElement('a');
                downloadLink.href = result.download_url;
                downloadLink.textContent = 'Download GPX File';
                downloadLink.classList.add('download-button'); // Optional: Add a CSS class
                downloadLink.download = ''; // Ensure it triggers a download
                resultDiv.appendChild(downloadLink);

                // Visualize the GPX file on the map
                addGpxToMap(result.download_url);
            } else {
                // Display the error message
                resultDiv.textContent = `Error: ${result.message}`;
            }
        } catch (error) {
            console.error('Error:', error);
            resultDiv.textContent = 'An unexpected error occurred.';
        }
    });

    // Initialize the map
    function initializeMap() {
        map = L.map('map').setView([51.1657, 10.4515], 6); // Centered on Germany
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
    }

    initializeMap();
});

function addGpxToMap(gpxUrl) {
    if (!map) initializeMap();

    const gpxLayer = new L.GPX(gpxUrl, {
        async: true,
        marker_options: {
            wptIconUrls: {
                '': '/static/images/pin-icon-wpt.png' // Correct path to the waypoint icon
            },
            shadowUrl: null // Disable the shadow
        }
    }).on('loaded', function (e) {
        console.log('GPX file loaded successfully:', gpxUrl);
        map.fitBounds(e.target.getBounds()); // Adjust the map view to fit the GPX data
    }).on('addpoint', function (e) {
        const latlng = e.point.getLatLng();
        const description = e.point.desc || 'No description available';
        L.marker(latlng).bindPopup(`<b>Description:</b> ${description}`).addTo(map);
    }).addTo(map);
}