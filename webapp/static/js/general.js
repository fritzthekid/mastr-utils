// This file contains the JavaScript code for the web application. 
// It handles user interactions, makes AJAX requests to the Flask backend, 
// and updates the UI based on the responses.

function setOpt(val) {
  document.getElementById('opts_hidden').value = val;
}

document.getElementById('mastr_file_autoupload').addEventListener('change', function(event) {
  const fileInput = event.target;
  const file = fileInput.files[0];
  const statusDiv = document.getElementById('upload-status');

  if (!file) return;

  const formData = new FormData();
  formData.append('mastr_file_name', file);
  formData.append('command', 'auto_upload');

  statusDiv.textContent = 'Upload läuft...';

  async function uploadFile() {
    try {
      const response = await fetch('/', {
          method: 'POST',
          body: formData
      });

      const result = await response.json();

      if (!response.ok) {
        if (result.status === 'panic') {
          console.log('panic detected, login again.')
          window.location.replace('/');
          throw new Error(result.message || 'Login expired, you will be thrown out.');
        } else {
          throw new Error(result.message || 'Upload fehlgeschlagen');
        }
      }


      statusDiv.textContent = '';
      document.getElementById('mastr_file_show').innerHTML = result.filename;
      document.getElementById('mastr_file_uploaded').value = result.filename;
    } catch (error) {
      statusDiv.innerHTML = '<pre style="color: red;">Error: ' + error.message + '</pre>';
    }
  }

  uploadFile();  // <<< Jetzt wird die Funktion auch tatsächlich ausgeführt!
});
