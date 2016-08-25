# These are required for the app to execute
export FLASK_APP=${FLASK_APP-"politi_hack.flask"}
export POLITI_HACK_CONFIG_PATH=${POLITI_HACK_CONFIG_PATH-$(readlink -m ./config.json)}
export PYTHONPATH=${PYTHONPATH-$(pwd)}
export PYTHONPATH=$PYTHONPATH:$(pwd)
