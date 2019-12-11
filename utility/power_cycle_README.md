# What is power_cycle.py?

`power_cycle.py` is a script that will turn the raspberry pi at a specified port off and then on.  
`power_cycle.py` is used by the restart and reinstall functions defined in `/../piman.py`  

# Why power_cycle.py?

`power_cycle.py` is needed to turn the raspberry pi's off and on remotely.  
To do this, `power_cycle.py` is designed to use the SNMP protocol to change an OID value in the MIB which will trigger a command to  
turn the pi's.  
When calling restart from `/../piman.py`, the pi will simply turn off and on.  
When calling reinstall from `/../piman.py`, the pi will try to network boot after turning off and on.  

# How does it work?

The __main__ function calls on a function:  
```python
def power_cycle(port):
    turn_off(port)
    time.sleep(1)
    turn_on(port)
```
Which will call 2 other functions in sequence.  

```python
def turn_off(port):
    print("Power_Cycle - Setting pi at port {} to OFF".format(port))
    errorIndication, errorStatus, errorIndex, varBinds = next(
        setCmd(
            SnmpEngine(),
            CommunityData("private@9", mpModel=0),
            UdpTransportTarget((switchAddress, 161)),
            ContextData(),
            ObjectType(
                ObjectIdentity("1.3.6.1.2.1.105.1.1.1.3.1." + str(port)), Integer(2)
            ),  # value of 2 turns the port OFF
        )
    )
```
The turn_off function will turn off the pi at the specified port.  

```python
def turn_on(port):
    print("Power_Cycle - Setting pi at port {} to ON".format(port))
    errorIndication, errorStatus, errorIndex, varBinds = next(
        setCmd(
            SnmpEngine(),
            CommunityData("private@9", mpModel=0),
            UdpTransportTarget((switchAddress, 161)),
            ContextData(),
            ObjectType(
                ObjectIdentity("1.3.6.1.2.1.105.1.1.1.3.1." + str(port)), Integer(1)
            ),  # value of 1 turns the port ON
        )
    )
```
The turn_on function will turn on the pi at the specified port  

#### About the OID...
The OID "1.3.6.1.2.1.105.1.1.1.3.1.x" where x is a specified port will serve as the trigger to turn the pi off or on.  
Using snmpwalk, you can find the INTEGER values of each port:
```bash
iso.3.6.1.2.1.105.1.1.1.3.1.1 = INTEGER: 1
iso.3.6.1.2.1.105.1.1.1.3.1.2 = INTEGER: 1
iso.3.6.1.2.1.105.1.1.1.3.1.3 = INTEGER: 1
iso.3.6.1.2.1.105.1.1.1.3.1.4 = INTEGER: 1
iso.3.6.1.2.1.105.1.1.1.3.1.5 = INTEGER: 1
iso.3.6.1.2.1.105.1.1.1.3.1.6 = INTEGER: 1
iso.3.6.1.2.1.105.1.1.1.3.1.7 = INTEGER: 1
iso.3.6.1.2.1.105.1.1.1.3.1.8 = INTEGER: 1
iso.3.6.1.2.1.105.1.1.1.3.1.9 = INTEGER: 1
...
```
If the value is 1: the pi will be turned on.  
If the value is 2: the pi will be turned off.  