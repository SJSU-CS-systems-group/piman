#!/bin/bash

cd --
python3 -m pip install bottle

cd /home/usr/local/piman/monitoring
python3 grafana.py logs/monitor.log