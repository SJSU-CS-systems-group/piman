#!/bin/bash
rm -rf build
PYTHONUSERBASE=$PWD/build python3 -m pip install click snmp
mkdir build/piman.app
mv build/lib/python*/site-packages/click build/piman.app
mv build/lib/python*/site-packages/snmp build/piman.app
cp -r utility tftp dhcp monitoring tcp *.py build/piman.app
python3 -m zipapp build/piman.app 
