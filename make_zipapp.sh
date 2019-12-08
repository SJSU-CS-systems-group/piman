#!/bin/bash
rm -rf build
mkdir build
PYTHONUSERBASE=$PWD/build python3 -m pip install --ignore-installed click pysnmp Flask
PYTHONUSERBASE=$PWD/build python3 -m pip install –-upgrade python-dotenv
mkdir build/piman.app
(
    cd build/lib/python*/site-packages
    mv $(ls | grep -v -) ../../../piman.app
)
cp -r utility tftp dhcp monitoring tcp *.py build/piman.app
mkdir build/piman.app/install
cp -r install/boot build/piman.app/install
cp -r config_ui build/piman.app/config_ui
# we don't want crypto stuff since it has native code
rm -r build/piman.app/Crypto*
python3 -m zipapp build/piman.app