import logging
import subprocess

import shared.config as config

log = logging.getLogger(__name__)

# Flask commands to run
FLASK_COMMAND = "python3 -m flask run --host={host_name} --port={port}".format(
    host_name=config.store['api_host']['name'],
    port=config.store['api_host']['port'],
)

print ("Flask Command: \"{flask_command}\"".format(flask_command=FLASK_COMMAND))
