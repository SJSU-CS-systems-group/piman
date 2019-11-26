# What is find_port.py?

`find_port.py` is a script that will search the network for the port that a raspberry pi is on.

# Why find_port.py?

Because the pi's are hosted on a virtual machine, find_port.py is a useful tool to remotely fetch the port that a pi is on.  
To do this, `find_port.py` is designed to take in the MAC address of the target pi, the ip address of the switch, and the VLAN address of the virtual network.  
`find_port.py` will use the SNMP protocol to look for the port that contains a device with the given MAC address.  
#### It is important to note that this implementation will be accessing a sysDesrc object using an OID, there is a chance that the output will not produce the port that the pi should be on due to an error in the pi's configuration. In that case, ask Prof. Ben.

# How does it work?

Before using SNMP, the MAC address will be converted from into an SNMP relevant format
```python
def mac_in_decimal(mac_address):
    parts = []
    for part in mac_address.split(":"):
        parts.append(str(int(part, 16)))
    return ".".join(parts)
```
The find_port function is as follows:
```python
def find_port(mac_address, switch_address, vlan_number):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(
            SnmpEngine(),
            CommunityData("public@{}".format(vlan_number), mpModel=0),
            UdpTransportTarget((switch_address, 161)),
            ContextData(),
            ObjectType(
                ObjectIdentity(
                    "1.3.6.1.2.1.17.4.3.1.2.{}".format(mac_in_decimal(mac_address))
                )
            ),
        )
    )
```
This section of the function will use an SNMP GET operation which will fetch a sysDescr.o object.  
Note that this is last year's implementation, which they sourced from: [http://snmplabs.com/pysnmp/quick-start.html]  
The port will be extracted and printed out in the following section of the function:  
```python
result = varBinds[0].prettyPrint()
return result.split(" = ")[1]
```
