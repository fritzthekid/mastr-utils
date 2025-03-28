// This file contains the JavaScript code for the web application. 
// It handles user interactions, makes AJAX requests to the Flask backend, 
// and updates the UI based on the responses.

document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('#convert-form');
    const resultDiv = document.querySelector('#result');
    const buttonsContainer = document.querySelector('.buttons-container');

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
                // Display success message
                resultDiv.innerHTML = `<p style="color: green;">${result.message}</p>`;

                // Create or update the "Download GPX File" button
                let downloadLink = document.querySelector('#download-gpx');
                if (!downloadLink) {
                    downloadLink = document.createElement('a');
                    downloadLink.id = 'download-gpx';
                    downloadLink.classList.add('button'); // Add the same CSS class as other buttons
                    buttonsContainer.appendChild(downloadLink);
                }
                downloadLink.href = result.download_url;
                downloadLink.textContent = 'Download GPX File';
                downloadLink.style.display = 'inline-block'; // Ensure the button is visible
            } else {
                // Display error message
                resultDiv.innerHTML = `<p style="color: red;">Error: ${result.message}</p>`;
            }
        } catch (error) {
            console.error('Error:', error);
            resultDiv.innerHTML = '<p style="color: red;">An unexpected error occurred.</p>';
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
    addGpxToMap('/tmp/xxx.gpx');
});

function addGpxToMap(gpxUrl) {
    if (!map) {
        console.error('Map is not initialized.');
        return;
    }

    const gpxLayer = new L.GPX(gpxUrl, {
        async: true,
        marker_options: {
            startIconUrl: null, // Disable the default start icon
            endIconUrl: null,   // Disable the default end icon
            shadowUrl: null     // Disable the shadow
        }
    }).on('loaded', function (e) {
        console.log('GPX file loaded successfully:', gpxUrl);
        map.fitBounds(e.target.getBounds()); // Adjust the map view to fit the GPX data
    }).on('addpoint', function (e) {
        const latlng = e.point.getLatLng();
        console.log('Waypoint added:', latlng); // Debugging: Log the waypoint coordinates
        const description = e.point.desc || 'No description available';
        L.marker(latlng).bindPopup(`<b>Description:</b> ${description}`).addTo(map);
    }).addTo(map);
}