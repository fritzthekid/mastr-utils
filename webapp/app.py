# from mastr_utils import Analyse
import os
import hashlib
from flask import Flask, request, jsonify, render_template, send_file 
from flask import redirect, url_for, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from mastr_utils.analyse_mastr import tmpdir
from mastr_utils.mastrtogpx import main as mtogpx
from mastr_utils.mastrtoplot import main as mtoplot

UPLOAD_FOLDER = f'{tmpdir}'
ALLOWED_EXTENSIONS = {'csv'}

checkpassword_crypt = '150b9efdf6e1c5b614b1e90cf7a17ca59b494b802e35f6ae467a540236d3ecaec7a27478fe1e9393'
global password_crypt
password_crypt = b""
global output_file
output_file = ""


app = Flask(__name__)
app.config['APPLICATION_ROOT'] = '/mastrutils'

application = DispatcherMiddleware(Flask('dummy'), {
    '/mastrutils': app
})

CORS(app)  # Enable CORS for all routes

MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 5 MB
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH


@app.errorhandler(RequestEntityTooLarge)
def handle_large_file(e):
    return jsonify({'status': 'error', 'message': f'The uploaded file exceeds max upload size: {int(MAX_CONTENT_LENGTH/1e6)} MB'}), 413

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
links = {
    "home":"index.html",
    "costs1":"kosten_atomkraft.html",
    "costs2":"kosten_energiewende.html",
    "battery":"batterien.html",
    "impressum":'impressum.html',
    "dataprotection":"datenschutzerklaerung.html"
}

@app.route('/', methods=['GET', 'POST'])
def index():
    global output_file
    if request.method == 'GET':
        if request.args.get("command") is not None:
            command = request.args.get("command")
            if command == "mastrtogpx":
                return render_template("mastrtogpx.html", debug=app.debug)
            elif command == "mastrtoplot":
                return render_template("mastrtoplot.html", debug=app.debug)
        print('Index page')
        return render_template('index.html', debug=app.debug)
    elif request.method=='POST':
        firstarg = [l for l in request.form][0]
        if firstarg in links:
            print(f"{links[firstarg]}")
            return show_page(links[firstarg])
        elif "mastrtogpx" in request.form:
            return render_template("mastrtogpx.html", debug=app.debug)
        elif "mastrtoplot" in request.form:
            return render_template("mastrtoplot.html", debug=app.debug)
        elif 'query' in request.form:
            # Verarbeitung für 'convert'
            return convert() # redirect(url_for('convert_function'))
        elif 'quera' in request.form:
            return plot()
        elif "downloadlog" in request.form:
            return download_log()
        elif "downloadfile" in request.form:
            return serve_tmp_file(output_file)
        print('Index page')
        return render_template('index.html')

@app.route('/mastrtogpx', methods=['GET', 'POST'])
def mastrtogpx():
    return render_template("mastrtogpx.html", debug=app.debug)

@app.route('/mastrtoplot', methods=['GET','POST'])
def mastrtoplot():
    return render_template("mastrtoplot.html", debug=app.debug)

def convert():
    global password_crypt
    global output_file
    try:
        # Retrieve POST arguments
        password = request.form.get('pwd') # password
        password_crypt = hashlib.shake_256(password.encode()).hexdigest(40)
        try:
            assert password_crypt == checkpassword_crypt
        except Exception as e:
            print(f'Password failed')
            return jsonify({'status': 'error', 'message': f"<Large><b>Password failed</b></Large>"})
        try:
            assert request.form.get("privacy") == "on"
        except:
            print(f'Password failed')
            return jsonify({'status': 'error', 'message': f"<Large><b>Haken zum hochladen fehlt</b></Large>"})
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
            output_file_basename = os.path.splitext(output_file_basename)[0]+".gpx"
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
            '-e',  # Energieträger
            '-l','[10000,5e7,3e5]',
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
    except Exception as e:
        print('Unexpected error:', e)
        return jsonify({'status': 'error', 'message': str(e)})

def plot():
    global password_crypt
    global output_file
    try:
        # Retrieve POST arguments
        password = request.form.get('pwd') # password
        password_crypt = hashlib.shake_256(password.encode()).hexdigest(40)
        try:
            assert password_crypt == checkpassword_crypt
        except Exception as e:
            print(f'Password failed')
            return jsonify({'status': 'error', 'message': f"<Large><b>Password failed</b></Large>"})
        try:
            assert request.form.get("privacy") == "on"
        except:
            print(f'Password failed')
            return jsonify({'status': 'error', 'message': f"<Large><b>Haken zum hochladen fehlt</b></Large>"})
        mastr_file = request.files.get('mastr_file')  # File upload
        quera = request.form.get('quera', '')  # Query parameter
        querb = request.form.get('querb', '')  # Query parameter
        querc = request.form.get('querc', '')  # Query parameter
        querd = request.form.get('querd', '')  # Query parameter
        quere = request.form.get('quere', '')  # Query parameter
        min_weight = request.form.get('min_weight', "0")  # Minimum weight
        radius = request.form.get('radius', 2000)  # Radius
        depends = request.form.get('depends', "Bundesland")  # Radius
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
            output_file_basename = os.path.splitext(output_file_basename)[0]+".svg"
            output_file = f"{tmpdir}/{output_file_basename}"
        else:
            output_file = f"{tmpdir}/{mastr_file.filename.rsplit('.', 1)[0]}.svg"

        if min_weight == "":
            min_weight = 0
        if len(depends) == 0:
            depends="Bundesland"

        # Debugging logs
        print(f'Mastr file: {file_path}')
        print(f'Query A: {quera}')
        print(f'Query B: {querb}')
        print(f'Query C: {querc}')
        print(f'Query D: {querd}')
        print(f'Query E: {quere}')
        print(f'Output: {output_file}')
        print('Converting...')

        # Run the conversion command

        query = quera
        if len(querb) > 0:
            query += f"#{querb}" 
        if len(querc) > 0:
            query += f"#{querc}" 
        if len(querd) > 0:
            query += f"#{querd}" 
        if len(quere) > 0:
            query += f"#{quere}" 
        command = [
            'mastrtoplot', file_path,
            '-q', query,
            '-d', depends,
            '-o', output_file,
            '-m', str(min_weight),
            '-r', str(radius),
            '-s',
            '-l','[10000,5e7,3e5]',
        ]

        print('Command:', ' '.join(command))
        # Capture stdout and stderr
        # result = subprocess.run(command, capture_output=True, text=True, check=True)
        mtoplot(command[1:])
        print('Conversion completed successfully.')

        return jsonify({
            'status': 'success',
            'message': 'Conversion completed successfully.',
            'download_url': f"/tmp/{output_file.rsplit('/', 1)[-1]}"
        })
    except AssertionError as e:
        print('assertion error:', e)
        return jsonify({'status': 'error', 'message': str(e)})
    except Exception as e:
        print('Unexpected error:', e)
        return jsonify({'status': 'error', 'message': str(e)})


def download_log():
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
        return jsonify({'status': 'error', 'message': f"Password failed"})
    try:
        basefile = os.path.basename(filename)
        if not os.path.isfile(f"{tmpdir}/{basefile}"):
            return jsonify({'status': 'error', 'message': f"File not found: check ending"})
        if filename.endswith(".gpx"):
            # Serve files from the tmpdir directory
            return send_from_directory(tmpdir, basefile, mimetype='application/gpx+xml')
        elif ( filename.endswith(".svg") or filename.endswith(".png") ) and ( len(request.args)>0 and request.args.get("command") == None ):
            # Serve files from the tmpdir directory
            return send_from_directory(tmpdir, basefile, mimetype='image/svg+xml')
        elif filename.endswith(".svg"):
            return send_from_directory(tmpdir, basefile, as_attachment=True, mimetype='application/xml')
        else:
            return jsonify({'status': 'error', 'message': 'File not found.'}), 404
    except FileNotFoundError:
        return jsonify({'status': 'error', 'message': 'File not found.'}), 404

def show_page(page):
    return render_template(page)

def impressum():
    return render_template('impressum.html')

if __name__ == '__main__':
    app.run(debug=True)
