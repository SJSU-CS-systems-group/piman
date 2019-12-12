#!/bin/bash
echo "run dhcp test"
./make_zipapp.sh
sudo python3 build/piman.pyz run-dhcp-test
