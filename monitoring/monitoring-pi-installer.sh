#!/bin/bash
sudo apt-get update
sudo apt -y install python3-pip

pip3 install flask-restful
pip3 install psutil

sudo cp monitoring-pi.service /etc/systemd/system
sudo systemctl enable monitoring-pi.service
sudo systemctl start monitoring-pi.service
systemctl status monitoring-pi.service
