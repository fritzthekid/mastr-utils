# from mastr_utils import Analyse
from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
from flask_cors import CORS
import subprocess
from mastr_utils.analyse_mastr import tmpdir
import logging  # Import logging to use the configuration from analyse_mastr.py

global password
password = ""
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/', methods=['GET', 'POST]'])
def index():
    if request.method == 'GET':
        print('Index page')
        return render_template('index.html', debug=app.debug)
    elif request.method=='POST':
        print('Index page')
        return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    global password
    try:
        # Retrieve POST arguments
        password = request.form.get('pwd') # password
        checkpassword=open(f"{tmpdir}/password.txt").read()
        try:
            assert password == checkpassword
        except Exception as e:
            print(f'Password failed: {password}, {checkpassword}')
            return jsonify({'status': 'error', 'message': f"Password failed:{e}"})
        mastr_file = request.files.get('mastr_file')  # File upload
        query = request.form.get('query', '')  # Query parameter
        color = 'x'  # request.form.get('color', 'Amber')  # Waypoint color
        min_weight = request.form.get('min_weight', "0")  # Minimum weight
        radius = request.form.get('radius', 2000)  # Radius
        output_file_basename = request.form.get('output_file', '').strip()  # Output file name

        # Save the uploaded file to the tmpdir location
        if not mastr_file:
            return jsonify({'status': 'error', 'message': 'No file uploaded.'}), 400

        file_path = f"{tmpdir}/{mastr_file.filename}"
        mastr_file.save(file_path)

        # Generate output file path
        if output_file_basename:
            output_file = f"{tmpdir}/{output_file_basename}"
        else:
            output_file = f"{tmpdir}/{mastr_file.filename.rsplit('.', 1)[0]}.gpx"

        if min_weight == "":
            min_weight = 0
        # Debugging logs
        print(f'Mastr file: {file_path}')
        print(f'Query: {query}')
        print(f'Output: {output_file}')
        print(f'Min weight: {min_weight}')
        print(f'Radius: {radius}')
        print('Converting...')

        # Run the conversion command
        command = [
            'mastrtogpx', file_path,
            '-q', query,
            '-o', output_file,
            '-c', color,
            '-m', str(min_weight),
            '-r', str(radius),
            '-e'  # Energieträger
        ]

        print('Command:', ' '.join(command))
        # Capture stdout and stderr
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print('Conversion completed successfully.')

        return jsonify({
            'status': 'success',
            'message': 'Conversion completed successfully.',
            'download_url': f"/tmp/{output_file.rsplit('/', 1)[-1]}"
        })
    except subprocess.CalledProcessError as e:
        print('Error during conversion:', e.stderr)
        return jsonify({'status': 'error', 'message': e.stderr})
    except Exception as e:
        print('Unexpected error:', e)
        return jsonify({'status': 'error', 'message': 'An unexpected error occurred.'})

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    global password
    checkpassword=open(f"{tmpdir}/password.txt").read()
    try:
        assert password == checkpassword
    except Exception as e:
        print(f'Password failed: {password}, {checkpassword}')
        return jsonify({'status': 'error', 'message': f"Password failed:{e}"})

    file_path = f"{tmpdir}/{filename}"
    try:
        return send_file(file_path, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'status': 'error', 'message': 'File not found.'}), 404

@app.route('/download-log', methods=['GET'])
def download_log():
    global password
    checkpassword=open(f"{tmpdir}/password.txt").read()
    try:
        assert password == checkpassword
    except Exception as e:
        print(f'Password failed: {password}, {checkpassword}')
        return jsonify({'status': 'error', 'message': f"Password failed:{e}"})
    if not app.debug:
        return jsonify({'status': 'error', 'message': 'No access rights to log-file.'}), 404
    log_file = f"{tmpdir}/mastr_analyse.log"  # Path to the log file
    try:
        return send_file(log_file, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'status': 'error', 'message': 'Log file not found.'}), 404

@app.route('/favicon.ico')
def favicon():
    return '', 204  # Return an empty response with a 204 No Content status

@app.route('/tmp/<path:filename>', methods=['GET'])
def serve_tmp_file(filename):
    global password
    checkpassword=open(f"{tmpdir}/password.txt").read()
    try:
        assert password == checkpassword
    except Exception as e:
        print(f'Password failed: {password}, {checkpassword}')
        return jsonify({'status': 'error', 'message': f"Password failed:{e}"})
    try:
        # Serve files from the tmpdir directory
        return send_from_directory(tmpdir, filename, mimetype='application/gpx+xml')
    except FileNotFoundError:
        return jsonify({'status': 'error', 'message': 'File not found.'}), 404

if __name__ == '__main__':
    app.run(debug=True)