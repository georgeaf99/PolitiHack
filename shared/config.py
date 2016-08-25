import json
import os

# Static variables for easy access
MAX_TWILIO_MSG_SIZE  = 1600
SERVICE_PHONE_NUMBER = "+18554164150"

with open(os.path.abspath(os.environ['POLITI_HACK_CONFIG_PATH']), "r") as f:
    store = json.loads(f.read())
