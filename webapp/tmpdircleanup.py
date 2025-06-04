import os
from datetime import datetime, timedelta
import shutil

tmpdir = f"{os.path.dirname(os.path.abspath(__file__))}/../tmp/anamastr"

def do_cleanup():
    for file in os.listdir(f"{tmpdir}"):
        filename = f"{tmpdir}/{file}"
        if os.path.isdir(filename):
            latest = os.path.getmtime(filename)
            if len(os.listdir(filename)) > 0:
                latest = max(os.path.getmtime(f"{filename}/{file}") for file in os.listdir(filename))
            if datetime.fromtimestamp(latest) < datetime.today() - timedelta(days=1):
                print(f'shutil.rmtree(f"{filename}")')
                shutil.rmtree(f"{filename}")

