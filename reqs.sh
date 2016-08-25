#!/bin/sh
source ./env.sh
if [ ! -e $POLITI_HACK_CONFIG_PATH ]; then
    echo "Error, PolitiHack config file not found:"
    echo "POLITI_HACK_CONFIG_PATH=$POLITI_HACK_CONFIG_PATH"
    exit 1
fi
pip3 install -r requirements.txt --upgrade
if [ $? -eq 0 ]; then
    echo "Pre-requisites to run PolitiHack are met."
    echo "To run, use ./run.sh"
fi
