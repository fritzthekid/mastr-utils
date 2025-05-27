// This file contains the JavaScript code for the web application. 
// It handles user interactions, makes AJAX requests to the Flask backend, 
// and updates the UI based on the responses.

function setOpt(val) {
  document.getElementById('opts_hidden').value = val;
}

document.getElementById('mastr_file_autoupload').addEventListener('change', function(event) {
  const fileInput = event.target;
  // const mastrfileNameDiv = document.getElementById('mastr_file_uploaded');
  const file = fileInput.files[0];
  const statusDiv = document.getElementById('upload-status');
  console.log("event on change");
  console.log(file);
  if (!file) return;

  const formData = new FormData();
  formData.append('mastr_file', file);
  formData.append('command', 'auto_upload');

  statusDiv.textContent = 'Upload läuft...';

  console.log('Upload läuft...');

  async function uploadFile() {
    try {
      const response = await fetch('/', {
          method: 'POST',
          body: formData
      });

      const result = await response.json();

      if (!response.ok) {
          throw new Error(result.message || 'Upload fehlgeschlagen');
      }


      statusDiv.textContent = '';
      document.getElementById('mastr_file_show').innerHTML = result.filename;
      //document.getElementById('mastr_file_show').innerHTML = result.filename;
      document.getElementById('mastr_file_uploaded').value = result.filename;
      console.log('Upload-Result:', result);
    } catch (error) {
      statusDiv.textContent = 'Error: ' + error.message;
      console.error(error);
    }
  }

  uploadFile();  // <<< Jetzt wird die Funktion auch tatsächlich ausgeführt!
});
