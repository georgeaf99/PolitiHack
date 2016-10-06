from decide_politics.flask import app

from flask import json
from flask import request
import jsonpickle


@app.route('/')
def health_check():
    return jsonpickle.encode(dict(healthy=True))
