#!/bin/bash

if [ -z "$3" ]
then
    echo "USAGE: $0 username password hosts_file"
    exit 1
fi

usnm=$1
pswd=$2
hosts=$3


while read -r line # Read hosts file one line at a time to get ip addresses of pis
do
    # Parse the line by replacing ; with spaces, then grabbing the ip address from the resulting array
    base=${line##*/}
    parsed_line="${line%/*}/${base//;/ }"
    array=($parsed_line)
    ip="${array[1]}"

    # Now check the status of each pi
    printf "Checking $usnm@$ip\n"
    sshpass -p $pswd ssh -n $usnm@$ip systemctl status monitoring-pi
    sleep 3 # Sleep so the user can get a chance to look at the output from each pi
    printf "\n\n"
done < $hosts
