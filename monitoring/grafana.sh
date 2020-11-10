#!/bin/bash

cd --
python3 -m pip install bottle



# checks for monitroing file path
# if not set, exits
if [[ -z "${MONITORING_LOG_PATH}" ]]; then
    echo "ERROR: MONITORING_LOG_PATH not set globally. Please reference the README.md and set the environ. var"
    echo "exiting..."
    exit 1
fi

cd /usr/local/piman/monitoring
python3 grafana.py ${MONITORING_LOG_PATH}