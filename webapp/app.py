# coding=utf-8
# from mastr_utils import Analyse
import os
import shutil
import json
import subprocess
from flask import Flask, request, jsonify, render_template, send_file 
from flask import redirect, url_for, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from flask import flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from mastr_utils.analyse_mastr import tmpdir, validatemarktstammdatenfile, logger
from mastr_utils.mastrtogpx import main as mtogpx
from mastr_utils.mastrtoplot import main as mtoplot
import mastr_utils
import numpy
import pandas
import matplotlib
import seaborn
import sklearn
print(mastr_utils.__version__)
print(numpy.__version__)
print(pandas.__version__)
print(matplotlib.__version__)
print(seaborn.__version__)
print(sklearn.__version__)
# from loginhandler import login, logout, adduser, changepw, userhandler

url_prefix = '/mastrutils'

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['APPLICATION_ROOT'] = url_prefix
app.config['SESSION_COOKIE_PATH'] = url_prefix

USER_FILE = f"{os.path.dirname(os.path.abspath(__file__))}/userdb.json"
SESSION_DATA_FILE = f"{os.path.dirname(os.path.abspath(__file__))}/session_data.json"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

CORS(app)  # Enable CORS for all routes

MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 5 MB
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH


def load_users():
    if not os.path.exists(USER_FILE):
        return {"admin": {"password":generate_password_hash("geheim")}}
    with open(USER_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f, indent=2)

users = load_users()

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

def userhandler():
    if not current_user.is_authenticated:
        return render_template('login.html')
    else:
        if current_user.id == "admin":
            return render_template("admin.html")
        return render_template("user.html", userprops = users[current_user.id], isowner = current_user.id == users[current_user.id]["owner"])

def make_sessiondir():
    session_dir = f"{tmpdir}/{session['id']}"
    if os.path.exists(session_dir):
        if os.path.isdir(session_dir):
            return session_dir
        else:
            shutil.rmtree(session_dir, ignore_errors=True)
    os.makedirs(session_dir, exist_ok=True)
    
def sessiondir():
    session_dir = f"{tmpdir}/{session['id']}"
    try:
        assert os.path.exists and os.path.isdir(session_dir), "session_dir does exists"
        return session_dir
    except:
        raise ValueError("tmp dir doesn't exists")

def show_login():
    return render_template('login.html')

def login():
    if request.method == 'POST':
        name = request.form['username']
        pw = request.form['password']
        logger.info(f"user: {name}, tried to log in")
        if name in users and check_password_hash(users[name]['password'], pw):
            login_user(User(name))
            if users[name]["status"] == "init":
                print(f"User {name} zunächst Passwort ändern.")
                logger.info(f"User {name} has to set initial password")
                flash(f'User {name} zunächst Passwort ändern.', category='message')
                return render_template('user.html', userprops = users[current_user.id], isowner = current_user.id == users[current_user.id]["owner"])
            login_user(User(name))
            session_data = load_session_data()
            session_data["id"] = session_data["id"]+1
            session["id"] = session_data["id"]
            save_session_data(session_data)
            make_sessiondir() # make sessiondir
            logger.info(f"user: {name}, successfully logged in, session[id]: {session_data['id']}")
            print(f"User {name} wurde eingeloggt. session[id]: {session_data['id']}")
            return redirect(url_for('index'))
        logger.info(f"User {name} or password not valid")
        flash('User oder Password nicht korrekt', category='message')
    return render_template('login.html')

@login_required
def logout():
    if not current_user.is_authenticated:
        logger.err("someone tried to logged out without been authentication")
        return render_template('403.html')
    logger.info(f"User {current_user.id} logged out")
    if not app.debug:
        try:
            shutil.rmtree(sessiondir())
        except:
            pass
    logout_user()
    return redirect(url_for('index'))

@login_required
def changepw(user = ""):
    if not current_user.is_authenticated:
        return render_template('403.html')
    logger.info(f"User {current_user.id} change password")
    if request.method == 'POST':
        old = request.form['old_password']
        new = request.form['new_password']
        retry = request.form["secondnew_password"]    
        if not check_password_hash(users[current_user.id]['password'], old):
            logger.info("old password does not fit")
            flash('Altes Passwort nicht korrekt', category='message')
            return render_template('user.html', userprops = users[current_user.id], isowner = current_user.id == users[current_user.id]["owner"])            # login_user(User(name))
        if new != retry:
            flash('Neues Password und Retry sind ungleich', category="message")
            return render_template('user.html', userprops = users[current_user.id], isowner = current_user.id == users[current_user.id]["owner"])
        else:
            users[current_user.id]['password'] = generate_password_hash(new)
            users[current_user.id]['status'] = "changed"
            save_users(users)
            logger.info(f"User {current_user.id} change password successfull")
            print(f"Passwurd korrekt.")
            return redirect(url_for('index'))
    return redirect(url_for('index'))    

@login_required
def adduserproperties():
    if not current_user.is_authenticated:
        return render_template('403.html')
    if request.method == 'POST':
        firstname = request.form['firstname']
        secondname = request.form['secondname']
        email = request.form["email"]    
        users[current_user.id]['firstname'] = firstname
        users[current_user.id]['secondname'] = secondname
        users[current_user.id]['email'] = email
        save_users(users)
        print(f"user properties for {current_user.id} changed.")
    return redirect(url_for('index'))    

@login_required
def adduser():
    if not current_user.is_authenticated or current_user.id != 'admin':
        return render_template('403.html')
    if request.method == 'POST':
        newuser = request.form['username']
        initpw = request.form['new_password']
        secondinitpw = request.form['secondnew_password']
        # if initpw != secondinitpw:
        #     flash('initpw und retry different')
        if initpw != secondinitpw:
            flash("initpw und retry ungleich",category="message")
        elif newuser not in users:
            users[newuser] = {
                "password": generate_password_hash(initpw), 
                "status":"init",
                "owner":"newuser",
            }
            save_users(users)
            flash(f'Benutzer {newuser} angelegt.', category="message")
        else:
            flash('Benutzer existiert bereits.', category="message")
    return render_template('admin.html')

# UPLOAD_FOLDER = f'{tmpdir}'
ALLOWED_EXTENSIONS = {'csv'}

def load_session_data():
    if not os.path.exists(SESSION_DATA_FILE):
        return {"id":0}
    with open(SESSION_DATA_FILE, 'r') as f:
        return json.load(f)

def save_session_data(session_data):
    with open(SESSION_DATA_FILE, 'w') as f:
        json.dump(session_data, f, indent=2)

users = load_users()
session_data = load_session_data()


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
    if current_user.is_authenticated:
        print(f"Is Authorized")
    else:
        print("not authorized")
    if request.method == 'GET':
        if request.args.get("command") is not None:
            command = request.args.get("command")
            if command == "mastrtogpx":
                if not current_user.is_authenticated:
                    return render_template("login.html", debug=app.debug)
                return mastrtogpx() #render_template("mastrtogpx.html", debug=app.debug)
            elif command == "mastrtoplot":
                if not current_user.is_authenticated:
                    return render_template("login.html", debug=app.debug) 
                return mastrtoplot() # render_template("mastrtoplot.html", debug=app.debug)
        print('Index page')
        return render_template('index.html', debug=app.debug)
    elif request.method=='POST':
        firstarg = [l for l in request.form][0]
        if firstarg in links:
            print(f"{links[firstarg]}")
            return show_page(links[firstarg])
        elif "command" in request.form:
            command = request.form["command"]
            if command == "mastrtogpx":
                return mastrtogpx()
            elif command == "convertx":
                optgpx()
            elif command == "mastrtoplot":
                return mastrtoplot()
            elif command == "plotx":
                return plot()
            elif command == "user":
                return userhandler()
            elif command == "show_login":
                return show_login()
            elif command == "login":
                return login()
            elif command == "changepw":
                return changepw()
            elif command == "adduserproperties":
                return adduserproperties()
            elif command == "adduser":
                return adduser()
            elif command == "logout":
                return logout()
            elif command == "auto_upload":
                return upload_mastr_file()
            return render_template('index.html', debug=app.debug)
        elif "mastrtogpx" in request.form:
            return mastrtogpx() #render_template("mastrtogpx.html", debug=app.debug)
        elif "mastrtoplot" in request.form:
            return mastrtoplot() #render_template("mastrtoplot.html", debug=app.debug)
        elif 'query' in request.form:
            # Verarbeitung für 'convert'
            return optgpx() # redirect(url_for('convert_function'))
        elif 'quera' in request.form:
            return plot()
        elif "downloadlog" in request.form:
            return download_log()
        elif "downloadfile" in request.form:
            return serve_tmp_file()
        print('Index page')
        return render_template('index.html', debug=app.debug)

# @app.route('/mastrtogpx', methods=['GET', 'POST'])
def mastrtogpx():
    if not current_user.is_authenticated:
        return render_template("login.html", debug=app.debug)
    try:
        sessiondir()
    except:
        logout()
        flash("User has been logged out, due to internal problems.")
        return render_template("login.html", debug=app.debug) 
    return render_template("mastrtogpx.html", debug=app.debug)

# @app.route('/mastrtoplot', methods=['GET','POST'])
# @login_required
def mastrtoplot():
    if not current_user.is_authenticated:
        return render_template("login.html", debug=app.debug)
    try:
        sessiondir()
    except:
        logout()
        flash("User has been logged out, due to internal problems.")
        return render_template("login.html", debug=app.debug)     
    return render_template("mastrtoplot.html", debug=app.debug)

def optgpx():
    if not current_user.is_authenticated:
        return jsonify({'status': 'panic', 'message':'Your session has expired, please login again.'}), 400
    try: 
        sessiondir()
    except:
        logout()
        return jsonify({'status': 'panic', 'message':'Your session has expired, please login again.'}), 400
    try:
        mastr_file = request.form.get('mastr_file')  # File upload

        # Save the uploaded file to the sessiondir() location
        if len(mastr_file) == 0:
            return jsonify({'status': 'error', 'message': 'No file uploaded.'}), 400
        file_path = f"{sessiondir()}/{mastr_file}"
        if not allowed_file(file_path):
            return jsonify({'status': 'error', 'message': 'only csv files as MaStR files are allowed.'}), 400
        print(f"tmpfile/mastr_file: {os.path.abspath(mastr_file)}")
        output_file_basename = request.form.get('output_file', '').strip() 

        if "opts" in request.form  and request.form.get("opts") == "help_queries":
            return help_queries(file_path,  f"{sessiondir()}/output.txt")
        elif "opts" in request.form and  request.form.get("opts") == "characteristics":
            return characteristics(file_path, f"{sessiondir()}/output.txt")
        elif "opts" in request.form  and request.form.get("opts") == "list-options":
            return listoptions(file_path,  f"{sessiondir()}/output.txt")

        # output_file_basename = request.form.get('output_file', '').strip()  # Output file name
        query = request.form.get('query', '')  # Query parameter
        color = 'x'  # request.form.get('color', 'Amber')  # Waypoint color
        min_weight = request.form.get('min_weight', "0")  # Minimum weight
        radius = request.form.get('radius', 2000)  # Radius
        if len(output_file_basename) > 0:
            output_file_basename = os.path.splitext(output_file_basename)[0]+".gpx"
            output_file = f"{sessiondir()}/{output_file_basename}"
        else:
            output_file = f"{sessiondir()}/{mastr_file.rsplit('.', 1)[0]}.gpx"

        if min_weight == "":
            min_weight = 0
        # Debugging logs
        print(f'Mastr file: {file_path}')
        print(f'Query: {query}')
        print(f'Output: {output_file}')
        print(f'Min weight: {min_weight}')
        print(f'Radius: {radius}')
        print('Converting...')

        command = ['mastrtogpx', file_path]
        if len(query) > 0:
            command += ['-q', query]
        command += [
            '-q', query,
            '-o', output_file,
            '-c', color,
            '-m', str(min_weight),
            '-r', str(radius),
            '-e',  # Energieträger
            '-l','[10000,5e7,3e5]',
        ]

        session["output_file"] = os.path.basename(output_file)
        print('Command:', ' '.join(command))
        # Capture stdout and stderr
        # result = subprocess.run(command, capture_output=True, text=True, check=True)
        mtogpx(command[1:])
        print('Conversion completed successfully.')
        return jsonify({
            'status': 'success',
            'message': 'Conversion completed successfully.',
            'download_url': f"./download" # tmp/{output_file.rsplit('/', 1)[-1]}"
        })
    except Exception as e:
        print('Unexpected error:', e)
        return jsonify({'status': 'error', 'message': str(e)})

def listoptions(file_path, output_file):
    command = [
        'mastrtogpx', 
        file_path,
        '-s',
        "-o",
        output_file,
        '-l','[10000,5e7,3e5]',
    ]
    print('Command:', ' '.join(command))
    # Capture stdout and stderr
    # result = subprocess.run(command, capture_output=True, text=True, check=True)
    mtogpx(command[1:])
    print('Conversion completed successfully.')
    message = open(output_file).read()
    return jsonify({
        'status': 'info',
        'message': message, #'Conversion completed successfully.',
        'download_url': f"./download" # tmp/{output_file.rsplit('/', 1)[-1]}"
    })


def characteristics(file_path, output_file):
    command = [
        'mastrtogpx', 
        file_path,
        '-a', 
        "-o",
        output_file,
        '-l','[10000,5e7,3e5]',
    ]
    print('Command:', ' '.join(command))
    # Capture stdout and stderr
    # result = subprocess.run(command, capture_output=True, text=True, check=True)
    mtogpx(command[1:])
    print('Characterics completed successfully.')
    message = open(output_file).read()
    return jsonify({
        'status': 'info',
        'message': message, 
        'download_url': f"./download" 
    })

def help_queries(file_path, output_file):
    message = """Hilfe für Query's, alle Query sind logische Ausdrücke der Form<br>
&nbsp;    SpaltenkopfA == "&lt;Wert&gt;" & SpaltenkopfB > Zahl (meist in kW)<br>
Typische Query's:
&nbsp;    (Energieträger == "Biomasse" | Energieträger == "Wind") <br>
dann gibt es einige spezielle Abkürzungen:<br>
&nbsp;    ge_1mw, (ge_10mw, ge_100mw): für BruttoleistungDerEinheit >= 1000 (10000, 100000)<br>
&nbsp;    lt_1mw: für BruttoleistungDerEinheit < 1000, ebso lt_10mw<br>
&nbsp;    is_active: füŕ BetriebsStatus == "In Betrieb"<br>
&nbsp;    is_pv: Energieträger == "Solare Strahlungsenergie"<br>
&nbsp;    is_battery: Speichertechnologie == "Batterie"<br>
die Spaltenköpfe sind alle unter "Hilfe -> list Options" zu finden.<br>
<br>
Zunächst ist es sinnvoll erstmal die charakteristischen Größen der Datei mit Hilfe->Characteristics zu ermitteln. 
"""
    return jsonify({
        'status': 'info',
        'message': message, 
        'download_url': f"./download" 
    })

#@login_required
def plot():
    if not current_user.is_authenticated:
        return jsonify({'status': 'panic', 'message':'Your session has expired, please login again.'}), 400
    try: 
        sessiondir()
    except:
        logout()
        return jsonify({'status': 'panic', 'message':'Your session has expired, please login again.'}), 400
    if not current_user.is_authenticated:
        return render_template("login.html", debug=app.debug)
    if not os.path.isdir(sessiondir()):
        logout()
        return render_template("login.html", debug=app.debug)
    try:
        mastr_file = request.form.get('mastr_file')  # File upload

        # Save the uploaded file to the sessiondir() location
        if not mastr_file:
            return jsonify({'status': 'error', 'message': 'No file uploaded.'}), 400
        file_path = f"{sessiondir()}/{mastr_file}"
        if not allowed_file(file_path):
            return jsonify({'status': 'error', 'message': 'only csv files as MaStR files are allowed.'}), 400
        print(f"tmpfile/mastr_file: {os.path.abspath(mastr_file)}")
        output_file_basename = request.form.get('output_file', '').strip()

        if "opts" in request.form  and request.form.get("opts") == "help_queries":
            return help_queries(file_path,  f"{sessiondir()}/output.txt")
        elif "opts" in request.form and  request.form.get("opts") == "characteristics":
            return characteristics(file_path, f"{sessiondir()}/output.txt")
        elif "opts" in request.form  and request.form.get("opts") == "list-options":
            return listoptions(file_path,  f"{sessiondir()}/output.txt")

        quera = request.form.get('quera', '')  # Query parameter
        querb = request.form.get('querb', '')  # Query parameter
        querc = request.form.get('querc', '')  # Query parameter
        querd = request.form.get('querd', '')  # Query parameter
        quere = request.form.get('quere', '')  # Query parameter
        # min_weight = request.form.get('min_weight', "0")  # Minimum weight
        # radius = request.form.get('radius', 2000)  # Radius
        depends = request.form.get('depends', "Bundesland")
        if output_file_basename:
            output_file_basename = os.path.splitext(output_file_basename)[0]+".svg"
            output_file = f"{sessiondir()}/{output_file_basename}"
        else:
            output_file = f"{sessiondir()}/{mastr_file.rsplit('.', 1)[0]}.svg"

        # if min_weight == "":
        #     min_weight = 0
        # if len(depends) == 0:
        #     depends="Bundesland"

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
            '-s',
            '-l','[10000,5e7,3e5]',
        ]

        session["output_file"] = os.path.basename(output_file)
        print('Command:', ' '.join(command))
        # Capture stdout and stderr
        # result = subprocess.run(command, capture_output=True, text=True, check=True)
        mtoplot(command[1:])
        print('Conversion completed successfully.')

        return jsonify({
            'status': 'success',
            'message': 'Conversion completed successfully.',
            'download_url': "./download" # f"/tmp/{output_file.rsplit('/', 1)[-1]}"
        })
    except AssertionError as e:
        print('assertion error:', e)
        return jsonify({'status': 'error', 'message': str(e)})
    except Exception as e:
        print('Unexpected error:', e)
        return jsonify({'status': 'error', 'message': str(e)})


def download_log():
    if not current_user.is_authenticated:
        render_template("login.html", debug=app.debug)
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

@app.route('/download', methods=['GET'])
def serve_tmp_file():
    if not current_user.is_authenticated:
        logger.err("someone tried to download file without been authentication")
        render_template("login.html", debug=app.debug)
    try:
        basefile = session.get("output_file")
        if basefile is None or basefile == "":
            return jsonify({'status': 'error', 'message': 'output_file not known.'}), 404
    except:
        logout()
        return jsonify({'status': 'error', 'message': 'trouble with output_file.'}), 404
    try:
        if not os.path.isfile(f"{sessiondir()}/{basefile}"):
            return jsonify({'status': 'error', 'message': f"File not found: check ending"})
        if basefile.endswith(".gpx"):
            # Serve files from the sessiondir() directory
            return send_from_directory(sessiondir(), basefile, mimetype='application/gpx+xml')
        elif ( basefile.endswith(".svg") or basefile.endswith(".png") ) and ( len(request.args)>0 and request.args.get("command") == None ):
            # Serve files from the sessiondir() directory
            return send_from_directory(sessiondir(), basefile, mimetype='image/svg+xml')
        elif basefile.endswith(".svg"):
            return send_from_directory(sessiondir(), basefile, as_attachment=True, mimetype='application/xml')
        else:
            return jsonify({'status': 'error', 'message': 'File not found.'}), 404
    except FileNotFoundError:
        logout()
        return jsonify({'status': 'error', 'message': 'File not found.'}), 404

def upload_mastr_file():
    if not current_user.is_authenticated:
        return jsonify({'status': 'panic', 'message':'Your session has expired, please login again.'}), 400
    try: 
        sessiondir()
    except:
        logout()
        return jsonify({'status': 'panic', 'message':'Your session has expired, please login again.'}), 400

    uploaded_file = request.files.get('mastr_file_name')
    if not uploaded_file:
        return jsonify({'status': 'error', 'message':'Keine Datei hochgeladen.'}), 400

    filename = secure_filename(uploaded_file.filename)
    if not allowed_file(uploaded_file.filename):
            return jsonify({'status': 'error', 'message': 'only csv files as MaStR files are allowed.'}), 400
    filepath = os.path.join(f"{sessiondir()}", filename)
    uploaded_file.save(filepath)
    try:
        validatemarktstammdatenfile(filepath)
    except ValueError as e:
        subprocess.call(["/usr/bin/shred", filepath])
        os.remove(filepath)
        logger.info(f"filepath: {e}")
        print(f"filepath: {e}")
        return jsonify({'status': 'error', 'message': f"{e}"}), 400
    return jsonify({
        'status': 'ok',
        'filename': filename,
        'size_kb': round(os.path.getsize(filepath) / 1024, 1)
    })



def show_page(page):
    return render_template(page)

def impressum():
    return render_template('impressum.html')

# Dispatcher Middleware zum Einbinden unter /mastrutils
application = DispatcherMiddleware(Flask('dummy'), {
    url_prefix: app
})


if __name__ == '__main__':
    app.config['SESSION_COOKIE_PATH'] = '/'
    app.run(debug=True, host="0.0.0.0", port=5000)
