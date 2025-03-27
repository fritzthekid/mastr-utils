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
            } else {
                // Display the error message
                resultDiv.textContent = `Error: ${result.message}`;
            }
        } catch (error) {
            console.error('Error:', error);
            resultDiv.textContent = 'An unexpected error occurred.';
        }
    });
});