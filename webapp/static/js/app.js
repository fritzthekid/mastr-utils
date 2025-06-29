// This file contains the JavaScript code for the web application. 
// It handles user interactions, makes AJAX requests to the Flask backend, 
// and updates the UI based on the responses.

document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('#convert-form');
    const resultDiv = document.querySelector('#result');
    const waitDiv = document.querySelector('#waitsection');

    form.addEventListener('submit', async function (event) {
        event.preventDefault(); // Prevent the default form submission

        // Clear result section (might be open from further call)
        resultDiv.innerHTML = '';
        // Wait annimation until plot is generated
        waitDiv.innerHTML = '<img style="-webkit-filter: grayscale(100%); filter: grayscale(100%);" src="static/images/Wait.gif">';
        // Prepare form data
        const formData = new FormData(form);

        try {
            // Send the form data to the server
            const response = await fetch('.', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.status === 'info') {
                waitDiv.innerHTML = '';
                resultDiv.innerHTML = `<p style="color: black;">${result.message}</p>`;
            } else if (result.status === 'panic') {
                console.log('panic detected, login again.')
                window.location.replace('/');
                throw new Error(result.message || 'Login expired, you will be thrown out.');
            } else if (result.status === 'success') {
                // Display success message
                waitDiv.innerHTML = '';
                resultDiv.innerHTML = `<p style="color: green;">${result.message}</p>`;

                // Add the download button
                /*const downloadLink = document.createElement('a');
                downloadLink.href = result.download_url;
                downloadLink.textContent = 'Download GPX File';
                downloadLink.classList.add('button'); // Use the same button style
                downloadLink.download = ''; // Ensure it triggers a download
                resultDiv.appendChild(downloadLink); */

                // Add the download button
                const downloadForm = document.createElement('form');
                downloadForm.className = "myform-white";
                downloadForm.method = "POST";
                const downloadbutton = document.createElement('button');
                downloadbutton.textContent = 'Download GPX File';
                downloadbutton.name = "downloadfile";
                downloadbutton.className = "buttons-container";
                downloadbutton.style = 
                "padding: 10px 20px;background-color: #4CAF50;color: white;border: none;border-radius: 5px;font-size: 16px;cursor: pointer;text-decoration: none;text-align: center;";
                downloadForm.appendChild(downloadbutton);
                resultDiv.appendChild(downloadForm);

                // Visualize the GPX file on the map
                addGpxToMap(result.download_url);
            } else {
                waitDiv.innerHTML = '';
                // Display error message with proper formatting
                resultDiv.innerHTML = `<pre style="color: red;">Error: ${result.message}</pre>`;
            }
        } catch (error) {
            waitDiv.innerHTML = '';
            console.error('Error:', error);
            resultDiv.innerHTML = '<pre style="color: red;">An unexpected error occurred.</pre>';
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

let currentGpxLayer = null; // Variable to track the current GPX layer

function addGpxToMap(gpxUrl) {
    if (!map) {
        console.error('Map is not initialized.');
        return;
    }

    // Remove all non-tile layers (e.g., markers, GPX layers)
    map.eachLayer(function (layer) {
        if (!(layer instanceof L.TileLayer)) {
            map.removeLayer(layer);
        }
    });

    // Add the new GPX layer
    const gpxLayer = new L.GPX(gpxUrl, {
        async: true,
        marker_options: {
            startIconUrl: '',
            endIconUrl: '',
            shadowUrl: '',
            wptIconUrls: {
                '': './static/images/mypin.png',
                'Navaid, Amber': './static/images/fire_unknown.svg',
                'Solare Strahlungsenergie': './static/images/solar.svg',
                'Biomasse': './static/images/greenpin.svg',
                'Speicher': './static/images/batterie.svg',
                'Wasser': './static/images/wasser.svg',
                'Wind': './static/images/wind.svg',
                'Geothermie': './static/images/greenpin.svg',
                'Steinkohle': './static/images/fire.svg',
                'Erdgas': './static/images/fire.svg',
                'andere Gase': './static/images/fire.svg',
                'Mineralölprodukte': './static/images/fire.svg',
            },
            iconSize: [32, 32],
            iconAnchor: [16, 32],
        }
    })
        .on('addpoint', function (e) {
            const point = e.point;
            const latlng = point._latlng || point.latlng;
            if (!latlng) return;

            const name = point.name || '';
            const desc = point.desc || ''; // Description from <desc>

            const popupContent = `<b>${name}</b><br>${desc}`;
            const icon = L.icon({
                iconUrl: `./static/images/graydot.svg`,
                iconSize: [16, 16],
                iconAnchor: [8, 16]
            });

            L.marker(latlng, { icon }).bindPopup(popupContent).addTo(map);
        })
        .on('loaded', function (e) {
            map.fitBounds(e.target.getBounds());
        })
        .addTo(map);

    // Update the current GPX layer
    currentGpxLayer = gpxLayer;
}
