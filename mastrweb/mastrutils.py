#from flask import Flask, render_template, request, redirect, url_for, session, flash
#from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
#from werkzeug.middleware.dispatcher import DispatcherMiddleware
import os
import shutil
import json
import logging
from flask import Flask, request, jsonify, render_template, send_file 
from flask import redirect, url_for, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from flask import flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from mastr_utils.analyse_mastr import tmpdir
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


# Konfiguration
url_prefix = '/mastrutils'

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['APPLICATION_ROOT'] = url_prefix
app.config['SESSION_COOKIE_PATH'] = url_prefix  # wichtig, damit das Cookie auch beim Prefix funktioniert
app.secret_key = 'supersecretkey'

# Login Setup
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

USER_FILE = f"{os.path.dirname(os.path.abspath(__file__))}/userdb.json"
SESSION_DATA_FILE = f"{os.path.dirname(os.path.abspath(__file__))}/session_data.json"

# Dummy User-Datenbank (Beispiel)
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
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

#--------
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



@app.route('/', methods=['GET', 'POST'])
# @login_required
def index():
    if current_user.is_authenticated:
        print(f"Is Authorized")

    else:
        print("not authorized")
    if request.method == 'GET':
        print(request.args)
        if request.args.get("command") is not None:
            pass
        return render_template('index.html') #, user=current_user.id)
    elif request.method == 'POST':
        print(request.form)
        if "command" in request.form:
            if request.form["command"] == "show_login":
                return show_login()
            elif request.form["command"] == "login":
                return login()
            elif request.form["command"] == "logout":
                print("command==logout")
                return logout()
    return render_template("index.html")

def show_login():
    return render_template("login.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['username']
        pw = request.form['password']
        if name in users and users[name]['password'] == pw:
            login_user(User(name))
            return redirect(url_for('index'))
        flash('Login fehlgeschlagen', category='message')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    print("do logout")
    logout_user()
    return redirect(url_for('login'))

@app.route('/debug')
def debug():
    return f"Session: {dict(session)}"

# Dispatcher Middleware zum Einbinden unter /mastrutils
application = DispatcherMiddleware(Flask('dummy'), {
    url_prefix: app
})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=3000)
