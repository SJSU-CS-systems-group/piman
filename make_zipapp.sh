#!/bin/bash
rm -rf build
mkdir build
PYTHONUSERBASE=$PWD/build python3 -m pip install --ignore-installed click pysnmp
mkdir build/piman.app
(
    cd build/lib/python*/site-packages
    mv $(ls | grep -v -) ../../../piman.app
)
cp -r utility tftp dhcp monitoring tcp *.py build/piman.app
mkdir build/piman.app/install
cp -r install/boot build/piman.app/install
# we don't want crypto stuff since it has native code
rm -r build/piman.app/Crypto*
python3 -m zipapp build/piman.app
