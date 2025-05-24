import os
from flask import jsonify
import sys
import re
import pytest

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/..")

from webapp import app

def test_app():
    assert app is not None
