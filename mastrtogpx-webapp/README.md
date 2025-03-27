# mastrtogpx Web Application

This project is a web application that provides a user-friendly interface for converting MaStR files to GPX files using the functionality of the `mastrtogpx` command. The application is built with Flask for the backend and HTML5, CSS, and JavaScript for the frontend.

## Project Structure

```
mastrtogpx-webapp
├── static
│   ├── css
│   │   └── styles.css       # CSS styles for the web application
│   ├── js
│   │   └── app.js           # JavaScript code for user interactions and AJAX requests
├── templates
│   └── index.html           # Main HTML page of the web application
├── app.py                   # Main Flask application
├── requirements.txt         # Python dependencies for the Flask application
└── README.md                # Documentation for the project
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd mastrtogpx-webapp
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Run the Flask application:**
   ```
   python app.py
   ```

5. **Access the web application:**
   Open your web browser and go to `http://127.0.0.1:5000`.

## Usage Guidelines

- The main page will provide a form where users can input the required parameters for the `mastrtogpx` command.
- Users can specify the path to the MaStR file, the query for filtering data, the output path for the GPX file, and other optional parameters.
- Upon submission, the application will process the input and return the generated GPX file for download.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for details.