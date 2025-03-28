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
            startIconUrl: '',
            endIconUrl: '',
            shadowUrl: '',
            // wptIcons: false,     // unterdrückt automatische Wegpunkt-Icons
            wptIconUrls: {
                'Navaid, Amber': '/static/images/dots.svg',  // verhindert Fehler
              },
            // wptIconUrls: {}      // verhindert fallback zu pin-icon-wpt.png
            iconSize: [16, 16],
            iconAnchor: [8, 16],
        }
        })
        .on('addpoint', function (e) {
        const point = e.point;
        const latlng = point._latlng || point.latlng;
        if (!latlng) return;
        
        const name = point.name || '';
        const desc = point.desc || '';  // Beschreibung aus <desc>
        
        const popupContent = `<b>${name}</b><br>${desc}`;
        
        const typ = point.meta?.type || 'default'; // falls du <type> verwendest
        const icon = L.icon({
            iconUrl: '/static/images/dots.svg', // `icons/${typ}.svg`,
            iconSize: [16, 16],
            iconAnchor: [8, 16]
        });
        
        L.marker(latlng, { icon }).bindPopup(popupContent).addTo(map);
        })
        .on('loaded', function (e) {
        map.fitBounds(e.target.getBounds());
        
        // Notfall: Standard-„Marker“-Marker entfernen, falls noch einer da ist
        map.eachLayer(layer => {
            if (layer instanceof L.Marker &&
                layer.getPopup()?.getContent?.() === 'Marker') {
            map.removeLayer(layer);
            }
        });
        })
        .addTo(map);          
    }
