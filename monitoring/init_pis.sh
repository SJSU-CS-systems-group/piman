#!/bin/bash

# Contributor: https://github.com/aaronsjsu
pswd="piman"
hosts="../hosts.csv"


while IFS= read -r line # Read hosts file one line at a time to get ip addresses of pis
do
    # Parse the line by replacing ; with spaces, then grabbing the ip address from the resulting array
    base=${line##*/}
    parsed_line="${line%/*}/${base//;/ }"
    array=($parsed_line)
    ip="${array[1]}"

    # Now run necessary commands
    echo "Setting up pi@$ip"
    sshpass -p $pswd scp monitoring-server.py monitoring-pi.service monitoring-pi.sh monitoring-pi-installer.sh pi@$ip:
    sshpass -p $pswd ssh -n pi@$ip ./monitoring-pi-installer.sh # Could run each pi in parallel with &
done < $hosts
