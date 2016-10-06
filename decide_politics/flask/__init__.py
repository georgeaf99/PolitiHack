import flask
import logging

app = flask.Flask(__name__)

logging.getLogger().setLevel(logging.INFO)

import decide_politics.endpoints.general
import decide_politics.endpoints.twillio_handler
import decide_politics.endpoints.web_client_handler
