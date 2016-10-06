# These are required for the app to execute
export FLASK_APP=${FLASK_APP-"decide_politics.flask"}
export POLITI_HACK_CONFIG_PATH=${POLITI_HACK_CONFIG_PATH-$(pwd)/config.json}
export PYTHONPATH=${PYTHONPATH-$(pwd)}
export PYTHONPATH=$PYTHONPATH:$(pwd)
