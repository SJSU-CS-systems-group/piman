#!/bin/bash

# To install the latest Enterprise edition
sudo apt-get install -y apt-transport-https
sudo apt-get install -y software-properties-common wget
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -

# Add this repository for stable releases
echo "deb https://packages.grafana.com/enterprise/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list

# After you add the repository
sudo apt-get update
sudo apt-get install grafana-enterprise

# start the server with systemd
sudo systemctl daemon-reload
sudo systemctl start grafana-server
sudo systemctl status grafana-server
