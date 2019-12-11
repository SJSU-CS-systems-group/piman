#!/bin/bash

# set up ip table for the pi
cd --
echo 1 > /proc/sys/net/ipv4/ip_forward
/sbin/iptables -t nat -A POSTROUTING -o ens3 -j MASQUERADE
/sbin/iptables -A FORWARD -i ens3 -o ens4 -m state --state RELATED,ESTABL$/sbin/iptables -A FORWARD -i ens4 -o ens3 -j ACCEPT

echo "----------------------PIMAN MONITOIRNG START---------------------"
# run the pi client keep asking monitoring data from each of the Pi
cd /usr/bin/piman/monitoring
python3 monitoring-client.py monitoring.config > logs/monitoring.log
