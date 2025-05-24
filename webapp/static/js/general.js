// This file contains the JavaScript code for the web application. 
// It handles user interactions, makes AJAX requests to the Flask backend, 
// and updates the UI based on the responses.

function setOpt(val) {
    console.log("setOpt: ".concat(val))
  document.getElementById('opts_hidden').value = val;
}
