#!/bin/bash

if [ -z "$4" ]
then
    echo "USAGE: $0 username password hosts_file monitoring_directory"
    exit 1
fi

usnm=$1
pswd=$2
hosts=$3
mdir=$4


while IFS= read -r line # Read hosts file one line at a time to get ip addresses of pis
do
    # Parse the line by replacing ; with spaces, then grabbing the ip address from the resulting array
    base=${line##*/}
    parsed_line="${line%/*}/${base//;/ }"
    array=($parsed_line)
    ip="${array[1]}"

    # Now run necessary commands
    echo "Setting up $usnm@$ip"
    sshpass -p $pswd scp $mdir/monitoring-server.py $mdir/monitoring-pi.service $mdir/monitoring-pi.sh $mdir/monitoring-pi-installer.sh $usnm@$ip:
    sshpass -p $pswd ssh -n $usnm@$ip ./monitoring-pi-installer.sh # Could run each pi in parallel with &
done < $hosts
