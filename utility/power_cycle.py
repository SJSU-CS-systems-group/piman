"""
This script will power cycle the raspberry pi's, causing them to attempt to PXE boot
snmp relevent OID = 1.3.6.1.2.1.105.1.1.1.3.1.x
where x = the port number to modify
setting to 1 will turn ON the port, setting to 2 will turn OFF the port
"""
from pysnmp.hlapi import *  # PySNMP library
import time  # For sleeping
from parse_config import config

private_number = config['private_number']

def power_cycle(switch_address, port):
    turn_off(switch_address, port)
    time.sleep(1)
    turn_on(switch_address, port)

def turn_off(switch_address, port):
    print("Power_Cycle - Setting pi at port {} to OFF".format(port))
    errorIndication, errorStatus, errorIndex, varBinds = next(
        setCmd(
            SnmpEngine(),
            CommunityData("private@"+str(private_number), mpModel=0),
            UdpTransportTarget((switch_address, 161)),
            ContextData(),
            ObjectType(
                ObjectIdentity("1.3.6.1.2.1.105.1.1.1.3.1." + str(port)), Integer(2)
            ),  # value of 2 turns the port OFF
        )
    )
    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print("Power_Cycle - not found")
    else:
        print("Power_Cycle - Set pi at port {} to OFF".format(port))


def turn_on(switch_address, port):
    print("Power_Cycle - Setting pi at port {} to ON".format(port))
    errorIndication, errorStatus, errorIndex, varBinds = next(
        setCmd(
            SnmpEngine(),
            CommunityData("private@"+str(private_number), mpModel=0),
            UdpTransportTarget((switch_address, 161)),
            ContextData(),
            ObjectType(
                ObjectIdentity("1.3.6.1.2.1.105.1.1.1.3.1." + str(port)), Integer(1)
            ),  # value of 1 turns the port ON
        )
    )
    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print("Power_Cycle - not found")
    else:
        print("Power_Cycle - Set pi at port {} to ON".format(port))

if __name__ == "__main__":
    power_cycle(10)
