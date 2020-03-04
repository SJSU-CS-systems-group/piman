from pysnmp.hlapi import *
from parse_config import config
import sys


#Reference SNMAP-WALK from:https://www.google.com/search?q=snmp+walk+solarwinds&oq=snmp+walk&aqs=chrome.5.69i57j0l5.2209j0j4&sourceid=chrome&ie=UTF-8

#.env file need to have VLAN number & Switch address

host = config['switches'][0]['swtich_0_address']
vlan = config['private_number']


def decToHexAddress(arg):
    arr = arg.split(".")
    output = ''

    for i in range(len(arr)):
        if i == len(arr) - 1:
            output = output + hex(int(arr[i])).replace('0x', '').upper()
        else:
            output = output + hex(int(arr[i])).replace('0x', '').upper() + ":"
    return output


def mac_mapper():
    print(host)
    print(vlan)
    output = []
    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(SnmpEngine(),
         CommunityData('private@'+str(vlan)), UdpTransportTarget((host, 161),timeout = 2, retries = 5), ContextData(),
         ObjectType(ObjectIdentity('1.3.6.1.2.1.17.4.3.1.2')), lexicographicMode=False):
        print("in for loop")
        if errorIndication:
            print("in error Indication")
            print(errorIndication, file=sys.stderr)
            break
        elif errorStatus:
            print("in error status")
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'),
                  file=sys.stderr)
            break
        else:
            print("no error, start mapping")
            data = []

            for varBind in varBinds:
                #data.append(str(varBind))
                print("inside varBind loop")
                element = str(varBind)
                print(element)
                element = element.replace("SNMPv2-SMI::mib-2.17.4.3.1.2.", "").replace(" = ", ";")
                splitArr = element.split(";")
                data.append(host + ',' + element.replace(splitArr[0],decToHexAddress(splitArr[0])))


            print("['SWITCH ADDRESS,MAC ADDRESS;PORT']")
            print(data)

        print("outside of if/else")
        output.extend(data)
     
    print("write to local file")
    text = ""
    for j in output:
        text += j + '\n'

    with open('mac_mapper.txt', "w") as f:
        f.write(text)


if __name__ == "__main__":
    mac_mapper()
