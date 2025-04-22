// This file contains the JavaScript code for the web application. 
// It handles user interactions, makes AJAX requests to the Flask backend, 
// and updates the UI based on the responses.

document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('#plot-form');
    const resultDiv = document.querySelector('#resultplot');

    form.addEventListener('submit', async function (event) {
        event.preventDefault(); // Prevent the default form submission

        // Clear previous results
        resultDiv.innerHTML = '';

        // Prepare form data
        const formData = new FormData(form);

        try {
            // Send the form data to the server
            const response = await fetch('/', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            if (result.status === 'success') {
                // Display success message
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
                downloadbutton.textContent = 'Download Plot File';
                downloadbutton.name = "downloadfile";
                downloadbutton.className = "buttons-container";
                downloadbutton.style = 
                "padding: 10px 20px;background-color: #4CAF50;color: white;border: none;border-radius: 5px;font-size: 16px;cursor: pointer;text-decoration: none;text-align: center;";
                downloadForm.appendChild(downloadbutton);
                resultDiv.appendChild(downloadForm);

                // Visualize the GPX file on the map
                addPlotToDiv(result.download_url);
            } else {
                // Display error message with proper formatting
                resultDiv.innerHTML = `<pre style="color: red;">Error: ${resultplot.message}</pre>`;
            }
        } catch (error) {
            console.error('Error:', error);
            resultDiv.innerHTML = '<pre style="color: red;">An unexpected error occurred.</pre>';
        }
    });

});

let currentImgPath = ''; // to keep the image

function addPlotToDiv(imgUrl) {
    const container = document.getElementById("map");
    container.innerHTML = ""; // Vorherige Inhalte entfernen
  
    const img = document.createElement("img");
    img.src = imgUrl;
    img.alt = "Gestapelte Bruttoleistung";
    img.style.maxWidth = "100%";
    img.style.maxHeight = "100%";
    container.appendChild(img);
    currentImgPath = imgUrl;
    //currentImg.img = img;
  }
  
  function popoutimg () {
    try {
        //console.log('do popoutimg');
        //console.log('Image Path:', currentImgPath);
        window.open(currentImgPath, '_black',focus())
    }
    catch (error) {
        console.error('Error:', error);
    }
  }
