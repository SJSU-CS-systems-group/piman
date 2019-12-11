# What is mac_mapper.py?

`mac_mapper.py` is a utility that will fetch the MAC address of a raspberry pi given a port number.  
The MAC address will also be written in a file called `mac_mapper.txt`.  

# Why is mac_mapper.py desgined like this?

`mac_mapper.py` is called from `../piman.py` as one of its provided functions.  
If a user knows the port number that a pi is on, they can use `mac_mapper.py` to find the MAC address of the pi and store it `mac_mapper.txt`.  
This way, the user will be able to produce a file with SWITCH_ADDRESS,MAC_ADDRESS;PORT_NUMBER tuples easily.  
`mac_mapper.py` was designed like this to provide a utility that works with `findport.py`, which will return the port number of a pi given its MAC address.  
Note that multiple ports can be used as the input for `mac_mapper.py` to fetch the MAC addresses of multiple pi's.  

# How does mac_mapper.py work?

When the user enters a port number using `../piman.py`'s mac_mapper function, `../pyman.py` will use `power_cycle.py` to restart the port.  
After a little while, `mac_mapper.py` will be called to provide the MAC address of the pi at the restarted port.  
When the MAC address is found, it will be written in `mac_mapper.py` along with the port number in a SWITCH_ADDRESS,MAC_ADDRESS;PORT_NUMBER tuple.  

### Function: mac_mapper()
_Description_: this function will use pysnmp to fetch an OID which it will use to retrieve the MAC address of a pi, then it will write the tuple in `mac_mapper.txt`.  
_Called by_: `piman.py` -> `mapper(port)` -> `mac_mapper.py` -> `__main__`  
_Return_: N/A  
```python
def mac_mapper():
    output = []
    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(SnmpEngine(),
         CommunityData('private@' + vlan), UdpTransportTarget((host, 161)), ContextData(),
         ObjectType(ObjectIdentity('1.3.6.1.2.1.17.4.3.1.2')), lexicographicMode=False):
        
        if errorIndication:
            print(errorIndication, file=sys.stderr)
            break
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'),
                  file=sys.stderr)
            break
        else:
            data = []

            for varBind in varBinds:
                #data.append(str(varBind))

                element = str(varBind)
                element = element.replace("SNMPv2-SMI::mib-2.17.4.3.1.2.", "").replace(" = ", ";")
                splitArr = element.split(";")
                data.append(host + ',' + element.replace(splitArr[0],decToHexAddress(splitArr[0])))


            print("['SWITCH ADDRESS,MAC ADDRESS;PORT']")
            print(data)

        output.extend(data)
    text = ""
    for o in output:
        text += o + '\n'

    with open('mac_mapper.txt', "w") as f:
        f.write(text)
```  
Walking through this function, we can see the pysnmp library used: 
```python
    ...
    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(SnmpEngine(),
         CommunityData('private@' + vlan), UdpTransportTarget((host, 161)), ContextData(),
         ObjectType(ObjectIdentity('1.3.6.1.2.1.17.4.3.1.2')), lexicographicMode=False):
    ...
```
What this call does is use snmpwalk to get an OID where the sysDesc matches the port number entered.  
The OID that is fetched will look something like this:  
```bash
iso.3.6.1.2.1.17.4.3.1.2.[Decimal MAC Address] = INTEGER: [Port Number]
```
Since the fetched OID will contain both the MAC address (in decimal form) and the port, the function will have to extract  
the `[Decimal MAC Address]` and `INTEGER: [Port Number]` from the OID. This is what the next part of the funnction does:  
```python
    ...
        data = []

        for varBind in varBinds:
            #data.append(str(varBind))

            element = str(varBind)
            element = element.replace("SNMPv2-SMI::mib-2.17.4.3.1.2.", "").replace(" = ", ";")
            splitArr = element.split(";")
            data.append(host + ',' + element.replace(splitArr[0],decToHexAddress(splitArr[0])))


        print("['SWITCH ADDRESS,MAC ADDRESS;PORT']")
        print(data)
    ...
```
After this step, the function will write down the SWITCH_ADDRESS,MAC_ADDRESS;PORT_NUMBER tuple into `mac_mapper.txt`.  

### Function: decToHexAddress(arg)
_Description_: this function will convert a decimal MAC address to a hexidecimal MAC address.  
_Called by_: `mac_mapper.py` -> `mac_mapper()` -> `decToHexAddress(arg)`  
_Return_: a MAC address in Hexidecimal form.    

| Type | Variable | Description |
|-------|-------|-------|
|String |arg |a decimal MAC address (XX.XX.XX.XX.XX.XX) |  
```python
def decToHexAddress(arg):
    arr = arg.split(".")
    output = ''

    for i in range(len(arr)):
        if i == len(arr) - 1:
            output = output + hex(int(arr[i])).replace('0x', '').upper()
        else:
            output = output + hex(int(arr[i])).replace('0x', '').upper() + ":"
    return output
```