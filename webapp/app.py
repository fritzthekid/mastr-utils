# from mastr_utils import Analyse
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import subprocess
from mastr_utils.analyse_mastr import tmpdir


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def index():
    print('Index page')
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    print('Converting...')
    
    # Handle file upload
    if 'mastr_file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file uploaded.'}), 400

    file = request.files['mastr_file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected.'}), 400

    # Save the uploaded file to a temporary location
    upload_folder = '/tmp'
    file_path = f"{upload_folder}/{file.filename}"
    file.save(file_path)
    print(f"Uploaded file saved to: {file_path}")

    # Retrieve other form data
    query = request.form.get('query', '')
    color = request.form.get('color', 'Amber')
    min_weight = request.form.get('min_weight', 0)
    radius = request.form.get('radius', 2000)
    output_file_basename = request.form.get('output_file', '').strip()

    # Generate output file path
    output_folder = '/tmp'
    if output_file_basename:
        output_file = f"{output_folder}/{output_file_basename}"
    else:
        output_file = f"{output_folder}/{file.filename.rsplit('.', 1)[0]}.gpx"

    # Debugging logs
    print(f'Mastr file: {file_path}')
    print(f'Query: {query}')
    print(f'Output: {output_file}')
    print(f'Color: {color}')
    print(f'Min weight: {min_weight}')
    print(f'Radius: {radius}')
    print('Converting...')

    query_part = ['-q', query]
    if query == '':
        query_part = []

    command = [
        'mastrtogpx', file_path,
    ] + query_part + [
        '-o', output_file,
        '-c', color,
        '-m', str(min_weight),
        '-r', str(radius)
    ]

    print('Command:', command)
    
    try:
        subprocess.run(command, check=True)
        print('Conversion completed successfully.')
        return jsonify({
            'status': 'success',
            'message': 'Conversion completed successfully.',
            'download_url': f"/download/{output_file.rsplit('/', 1)[-1]}"
        })
    except subprocess.CalledProcessError as e:
        print('Error:', e)
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    output_folder = '/tmp'
    file_path = f"{output_folder}/{filename}"
    try:
        return send_file(file_path, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'status': 'error', 'message': 'File not found.'}), 404

@app.route('/download-log', methods=['GET'])
def download_log():
    log_file = f"{tmpdir}/mastr_analyse.log"  # Path to the log file
    try:
        return send_file(log_file, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'status': 'error', 'message': 'Log file not found.'}), 404

@app.route('/favicon.ico')
def favicon():
    return '', 204  # Return an empty response with a 204 No Content status

if __name__ == '__main__':
    app.run(debug=True)