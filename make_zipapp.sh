#!/bin/bash
if [[ $UID -eq 0 ]]
then
   echo "Do not run $0 as root"
   exit 2
fi
rm -rf build
mkdir build
PYTHONUSERBASE=$PWD/build python3 -m pip install --ignore-installed click pysnmp serializeme Flask python-dotenv PyYAML
mkdir build/piman.app
(
    cd build/lib/python*/site-packages
    mv $(ls | grep -v -) ../../../piman.app
)
cp -r logging.conf utility tftp dhcp monitoring tcp dns *.py build/piman.app
mkdir build/piman.app/install
mkdir build/logs
cp piman.yaml build
#git clone --depth 1 --single-branch https://github.com/raspberrypi/firmware.git firmware
if [ ! -f firmware/boot/bootcode.bin ]
then
    git submodule init firmware
    git submodule update --depth 1 firmware
fi


mkdir -p build/piman.app/install/boot
cp -r firmware/boot build/piman.app/install/
cp -r install/boot build/piman.app/install/
cp -r config_ui build/piman.app/config_ui
cp dhcp/addr_database.csv build/piman.app/install
# we don't want crypto stuff since it has native code
rm -r build/piman.app/Crypto*
python3 -m zipapp build/piman.app
