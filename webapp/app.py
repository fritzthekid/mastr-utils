# from mastr_utils import Analyse
import os
import hashlib
from flask import Flask, request, jsonify, render_template, send_file 
from flask import redirect, url_for, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge
from mastr_utils.analyse_mastr import tmpdir
from mastr_utils.mastrtogpx import main as mtogpx

UPLOAD_FOLDER = f'{tmpdir}'
ALLOWED_EXTENSIONS = {'csv'}

checkpassword_crypt = '150b9efdf6e1c5b614b1e90cf7a17ca59b494b802e35f6ae467a540236d3ecaec7a27478fe1e9393'
global password_crypt
password_crypt = b""
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

MAX_CONTENT_LENGTH = 15 * 1024 * 1024  # 5 MB
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH


@app.errorhandler(RequestEntityTooLarge)
def handle_large_file(e):
    return jsonify({'status': 'error', 'message': f'The uploaded file exceeds max upload size: {int(MAX_CONTENT_LENGTH/1e6)} MB'}), 413

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST]'])
def index():
    if request.method == 'GET':
        print('Index page')
        return render_template('index.html', debug=app.debug)
    elif request.method=='POST':
        if 'convert' in request.form:
            # Verarbeitung für 'convert'
            return redirect(url_for('convert_function'))
        # elif 'download' in request.form:
        #     filename = request.form.get('filename')
        #     # Verarbeitung für 'download/filename'
        #     return redirect(url_for('download_function', filename=filename))
        print('Index page')
        return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    global password_crypt
    try:
        # Retrieve POST arguments
        password = request.form.get('pwd') # password
        password_crypt = hashlib.shake_256(password.encode()).hexdigest(40)
        try:
            assert password_crypt == checkpassword_crypt
        except Exception as e:
            print(f'Password failed: {hashlib.shake_256(password.encode()).hexdigest(40)}, {checkpassword}')
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
        if not allowed_file(file_path):
            return jsonify({'status': 'error', 'message': 'only csv files as MaStR files are allowed.'}), 400
        print(f"tmpfile/mastr_file: {os.path.abspath(mastr_file.filename)}")
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
        # result = subprocess.run(command, capture_output=True, text=True, check=True)
        mtogpx(command[1:])
        print('Conversion completed successfully.')

        return jsonify({
            'status': 'success',
            'message': 'Conversion completed successfully.',
            'download_url': f"/tmp/{output_file.rsplit('/', 1)[-1]}"
        })
    # except subprocess.CalledProcessError as e:
    #     print('Error during conversion:', e.stderr)
    #    return jsonify({'status': 'error', 'message': e.stderr})
    except Exception as e:
        print('Unexpected error:', e)
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    global password_crypt
    try:
        assert password_crypt == checkpassword_crypt
    except Exception as e:
        print(f'Password failed: {password_crypt}, {checkpassword_crypt}')
        return jsonify({'status': 'error', 'message': f"Password failed:{e}"})

    file_path = f"{tmpdir}/{filename}"
    try:
        return send_file(file_path, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'status': 'error', 'message': 'File not found.'}), 404

@app.route('/download-log', methods=['GET'])
def download_log():
    global password_crypt
    try:
        assert password_crypt == checkpassword_crypt
    except Exception as e:
        print(f'Password failed: {password_crypt}, {checkpassword_crypt}')
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
    global password_crypt
    try:
        assert password_crypt == checkpassword_crypt
    except Exception as e:
        print(f'Password failed: {password_crypt}, {checkpassword_crypt}')
        return jsonify({'status': 'error', 'message': f"Password failed:{e}"})
    try:
        # Serve files from the tmpdir directory
        return send_from_directory(tmpdir, filename, mimetype='application/gpx+xml')
    except FileNotFoundError:
        return jsonify({'status': 'error', 'message': 'File not found.'}), 404

@app.route('/energie_kostenvergleich', methods=['GET'])
def show_energiekostenvergleichsanalyse():
    return render_template('energie_kostenvergleich.html')

@app.route('/impressum', methods=['GET'])
def impressum():
    return render_template('impressum.html')

if __name__ == '__main__':
    app.run(debug=True)