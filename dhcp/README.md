# DHCP

## Navigation    
[What is dhcp.py?](##What-is-dhcp.py?)   
[Why dhcp.py is designed like this?](##Why-dhcp.py-is-designed-like-this?)   
[How does dhcp.py work?](##How-does-dhcp.py-work?)   
[Classes and Functions Definitions](##Classes-and-Functions-Definitions)   
*Unfortunately, BitBucket has not fixed header-linking in the README's. Please use `Ctrl + F` to find things in here.*    

## What is dhcp.py?
This file is meant to create, offer, and assign IP addresses when given the MAC address inside the `hosts.csv`, created and located in the root directory of this repository ***upon execution*** of `piman.py`. 

## Why dhcp.py is designed like this?
Due to security purposes set from the team before, we must manually add the MAC addresses into the `hosts.csv` since we do not want malicious random hardware to come into contact with our server from the server room (since anyone can go in there as they please and add their own hardware a.k.a ***insider threat***). This is not exactly like a DHCP server and we take a few shortcuts here. In this server, we will either receive MAC addresses first, or DHCPDISCOVERY packets if the Raspberry Pi's are installed, and `dhcp.py` will send a DHCPOFFER packet to the RPi. If the RPi takes the DHCPOFFER (which includes the IP address), it will send a DHCPREQUEST and stop there and operate with that IP address - there will be no DHCPACK afterwards (this is the shortcut). For the MAC addresses in the `hosts.csv`, it must be added in this format:

| MAC Address | IP Address | Device's Name | Timestamp |
|-------|-------|-------|-------|
|B8:27:EB:23:89:E3|172.30.9.8|raspberrypi|1571097294

Each of these attributes are separated by **semi-colons**. In the first part, it is the MAC address of the Raspberry Pi. The second part is the IP address that the DHCP will give, or what the Pi will request if it was previously given an IP address from the DHCP server. The third part is the name the Raspberry pi (this will only show if you have installed the Pi, or has been installed before). The last part is the timestamp according to Linux epoch times. Therefore, all you really need is the MAC address and the rest may be empty or filled like so:
```
B8:27:EB:23:89:E3;0.0.0.0;;    

--OR--    

B8:27:EB:23:89:E3;172.30.9.11;raspberrypi;1571097294
``` 


## How does dhcp.py work?
Everything below will detail how each function works according to class and it's functionalities. It is ***highly recommended*** that you step through the code to see how it works and immediately ask for clarification for what everything does since the documentation may not be concise in definition. If you would like to see the packets being sent "live", we recommend executing this command below in a separate terminal to monitor the network. Please refer to the [manpages](https://linux.die.net/man/8/tcpdump) for more uses.    
```tcpdump -i ens4```

We are executing this command assuming that you have the following pre-conditions:

1. That you are logged into the Pi Manager's Virtual Machine (VM) via `ssh`.
2. You are using the *bash shell* to execute these commands.
3. We are assuming that `ens4` is the switch's (the switch that contains all the RPi's) IP address. Otherwise, change accordingly in `.env` file. If you do not see the switch's IP address please inform your supervisor. Execute this following command in the VM to verify:            
```ifconfig```


## **Classes and Functions Definitions**
---
This is how the following documentation will be formatted:
```
Class
Function In Class
1. Brief description
2. Called by whom
3. Return values
4. Related Classes and functions
5. Code block (Only Global / Public Functions)
```    
Only the necessary and used functions, in order to grasp what DHCP is doing, will be documented. (**Warning**: there are *SEVERAL* instance variables and functions that do not return anything)       


### **Global / Public Functions** 
#### Function: do_dhcp(ip, subnet_mask, mac_ip_file)
*Description*:   
Initializes the DHCPServer with values set by `piman.py`. Host file is also set to the `hosts.csv` so it may update the values as stated above. A set lease time is given as per protocol. For the available IP addresses, it sets up from 11-20 in network filter and continues to listen for requests continuously.    

*Called by*:    
`piman.py` -> `server()`  

*Return*: None   

| Type | Variable | Description |
|-------|-------|-------|
|String | ip | IP address of the Pi Manager's IP |
|String | subnet_mask | Subnet mask given from `piman.py` |
|String | mac_ip_file | Name of the csv file storing the manual inputted MAC addresses | 


Related Classes and functions: [DHCPServerConfiguration](###DHCPServerConfiguration), [DHCPServer](###DHCPServer), NETWORK
```python
def do_dhcp(ip, subnet_mask, mac_ip_file):
    configuration = DHCPServerConfiguration(ip, subnet_mask)
    configuration.host_file = mac_ip_file
    configuration.ip_address_lease_time = 1296000
    server = DHCPServer(configuration)
    for ip in server.configuration.all_ip_addresses():
        assert ip == server.configuration.network_filter()
    print("DHCP server is running...")
    server.run()
```

#### Function: network_from_ip_subnet(ip, subnet_mask)
*Description*:   
Receives the network address from the given IP address and subnet mask.    

*Called by*:    
`dhcp.py` -> `DHCPServerConfiguration` -> `__init__(self,ip,subnet_mask)`  

*Return*: (String) Network Address      

| Type | Variable | Description |
|-------|-------|-------|
| String | ip | IP address of the Pi Manager's IP |
| String | subnet_mask | Subnet mask given from `piman.py` |

Related Classes and functions: [DHCPServerConfiguration](#DHCPServerConfiguration), [DHCPServer](###DHCPServer), NETWORK
```python
def network_from_ip_subnet(ip, subnet_mask):
    import socket
    subnet_mask = struct.unpack('>I', socket.inet_aton(subnet_mask))[0]  # Convert to 32 bit format (unsigned int) to perform AND operation
    ip = struct.unpack('>I', socket.inet_aton(ip))[0]
    network = ip & subnet_mask
    return socket.inet_ntoa(struct.pack('>I', network)) # Convert back to IP string
```


#### Function: ip_addresses(network, subnet_mask)
*Description*:   
Receives valid ip addresses from the network address, you can use this to assign a specific IP address range.    

*Called by*:    
`dhcp.py` -> `DHCPServerConfiguration` -> `all_ip_addresses(self)`  

*Return*: (Iterator) String of valid IP addresses      

| Type | Variable | Description |
|-------|-------|-------|
| String | network | Network address of the Pi Manager's IP take from network_from_ip_subnet(ip, subnet_mask) |
| String | subnet_mask | Subnet mask given from `piman.py`  |

Related Classes and functions: [DHCPServerConfiguration](#DHCPServerConfiguration)
```python
def ip_addresses(network, subnet_mask):
    import socket, struct
    subnet_mask = struct.unpack('>I', socket.inet_aton(subnet_mask))[0]
    network = struct.unpack('>I', socket.inet_aton(network))[0]
    network = network & subnet_mask
    start = network + 1
    end = (network | (~subnet_mask & 0xffffffff))
    return (socket.inet_ntoa(struct.pack('>I', i)) for i in range(start, end))
```


#### Function: sorted_hosts(hosts)
*Description*:   
Sorts all the IP addresses from a given Host 

*Called by*:    
`dhcp.py` -> `DHCPServer` -> `get_all_hosts(self)`
`dhcp.py` -> `DHCPServer` -> `get_current_hosts(self)`    

*Return*: (Iterator) String of valid IP addresses         

| Type | Variable | Description |
|-------|-------|-------|
| List | hosts | List of hosts given from the `hosts.csv` file with following pattern array: [mac, ip, hostname, last_used] |

Related Classes and functions: [HostDatabase.get(self, **kw)](###HostDatabase), Host, ALL, [CSVDatabase.get(self, pattern)](###CSVDatabase), 
```python
def sorted_hosts(hosts):
    hosts = list(hosts)
    hosts.sort(key = lambda host: (host.hostname.lower(), host.mac.lower(), host.ip.lower()))
    return hosts
```
---

### **WriteBootProtocolPacket**
#### Function: __init__(self, configuration)
*Description*:   
Initializes the name of the tftp server name as the IP address of the DHCP server. Checkout **`listener.py`** and look at the different options its setting. All the options are saved into `self.names` (but not used).

*Called by*:    
`dhcp.py` -> `Transaction` -> `send_offer(self, discovery)`   
`dhcp.py` -> `Transaction` -> `acknowledge(self, discovery)`   

*Return*: (Type) Description of object         

| Type | Variable | Description |
|-------|-------|-------|
| DHCPServerConfiguration | configuration | Description of the argument and what it is |

Related Classes and functions: [Transaction](###Transaction), ReadBootProtocolPacket      

#### Function: to_bytes(self)
*Description*:   
Converts integer 236 into a byte array then sets the instance variables to those specific bytes and converts it back into byte form. Those instance variables are packed into a 32-bit format first before being assigned to those bytes - writing the packet for transport.

*Called by*:    
`dhcp.py` -> `DHCPServer` -> `broadcast(self, packet)`        

*Return*: (Bytes) Packet          

#### Function: get_option(self, option)
*Description*:   
Again, checkout the `listener.py`. This will return the value from those tuples in the options list.

*Called by*:    
`dhcp.py` -> `WriteBootProtocolPacket` -> `to_bytes(self)`  

*Return*: (String) Name of the option from options in `listener.py`         

| Type | Variable | Description |
|-------|-------|-------|
| Any | option | One of the values from 3-tuple from `options` in `listener.py` |

Related Classes and functions: ReadBootProtocolPacket       

#### Function: options(self)
*Description*:   
Initialize a empty list. The variable `parameter_order` is filled by the packet sent from the client which contains varying options like those listed in `listener.py`. If the option in `parameter_order` is in `listener.py`'s `options`, then it will add it to the list. The next part will add the attribute of that first variable in the 3-tuple if it's not in done for each `options`. The next part is a guess; however, it will append to the list if that specified function is not in the list.  

*Called by*:    
`dhcp.py` -> `WriteBootProtocolPacket` -> `to_bytes`  

*Return*: (List) List of 3-tuples         

Related Classes and functions: ReadBootProtocolPacket              

#### Function: __str__(self)
*Description*:   
Converts bytes packet into a string type format 

*Called by*:    
None      

*Return*: (String) String representation of the WriteBootProtcolPacket          

Related Classes and functions: [ReadBootProtocolPacket]()      

---
### **DelayWorker**
#### Function: __init__(self)
*Description*:   
Initialize with a priority queue and running a thread to delay response.

*Called by*:    
`dhcp.py` -> `DelayWorker` -> `__init__(self)`       

*Return*: None      

Related Classes and functions: [DHCPServer](###DHCPServer), [Transaction](###Transaction)     

#### Function: _delay_response_thread(self)
*Description*:   
Put the current thread to sleep for a millisecond to delay response.

*Called by*:    
`dhcp.py` -> `DelayWorker` -> `__init__(self)`    

*Return*: None      

#### Function: do_after(self, seconds, func, args = (), kw = {})
*Description*:   
Places in queue for DelayWorker's thread to delay the response by `seconds` before execution of `func`. This is a higher-order function.

*Called by*:    
`dhcp.py` -> `Transaction` -> `receive(self,packet)`  

*Return*: None      

| Type | Variable | Description |
|-------|-------|-------|
| Integer | seconds | How many seconds to delay before execution of `func` |       
| Function | func | Function to execute later on after the delay |       
| Tuple | args | Tuple depending on how many parameters `func` has |       

Related Classes and functions: [DelayWorker](###DelayWorker), [Transaction](###Transaction)             

#### Function: close(self)
*Description*:   
Sets the boolean to True for private variable `self.close` so the DelayWorker's thread closes and exits.

*Called by*:    
`dhcp.py` -> `DHCPServer` -> `close(self)`  

*Return*: None      

Related Classes and functions: [DHCPServer](###DHCPServer), [Transaction](###Transaction)     

---
### **Transaction**
#### Function: __init__(self, server)
*Description*:   
Initializes Transaction object with `DHCPServer` object's properties which include: DelayWorker and DHCPServerConfiguration instance variable properties.

*Called by*:    
`dhcp.py` -> `DHCPServer` -> `__init__(self, configuration = None)`  

*Return*: None      

| Type | Variable | Description |
|-------|-------|-------|
| DHCPServer | server | DHCPServer object with DelayWorker and DHCPServerConfiguration properties |

Related Classes and functions: [DHCPServer.received()](###DHCPServer)    

#### Function: is_done(self)
*Description*:   
Check to see if the Transaction is done between the client and server regarding the DHCP protocol, this will set as True

*Called by*:    
`dhcp.py` -> `Transaction` -> `received_dhcp_request()`  
`dhcp.py` -> `DHCPServer` -> `update(self, timeout = 0)`  

*Return*: (Boolean) True if `self.done` is set as True or `self.done_time` is less than the timer      

Related Classes and functions: [DHCPServer.update(self, timeout = 0)]()     

#### Function: close(self)
*Description*:   
Sets boolean value of `self.done` to True so the next time functions call `is_done(self)` it will close the Transaction Object.

*Called by*:    
`dhcp.py` -> `Transaction` -> `send_offer(self, discovery)`    
`dhcp.py` -> `Transaction` -> `receieved_dhcp_request(self, request)`     
`dhcp.py` -> `Transaction` -> `receieved_dhcp_inform(self, inform)`    

*Return*: None      

Related Classes and functions: [WriteBootProtocolPacket](###WriteBootProtocolPacket)     

#### Function: receive(self, packet)
*Description*:   
When a packet has been received, the following could happen:    
If received a *DHCPDISCOVER*, execute `Transaction.received_dhcp_discover(self, packet)`    
If received a *DHCPREQUEST*, execute `Transaction.received_dhcp_request(self, packet)`    
If received a *DHCPINFORM*, execute `Transaction.received_dhcp_inform(self, packet)`    

*Called by*:    
`dhcp.py` -> `DHCPServer` -> `received()`  

*Return*: (Boolean) True if the packet message type is DHCPDISCOVER, DHCPREQUEST, or DHCPINFORM; otherwise, False     

| Type | Variable | Description |
|-------|-------|-------|
| ReadBootProtocolPacket | packet | Object that contains the MAC address, requested IP address, device's host name or '', and the timestamp |

Related Classes and functions: [DHCPServer](###DHCPServer), [WriteBootProtocolPacket](###WriteBootProtocolPacket)     

#### Function: received_dhcp_discover(self, discovery)
*Description*:   
If the DHCPDISCOVERY packet was sent by a known host from `hosts.csv`, a DHCPOFFER will be sent by using the function `Transaction.send_offer(self, discovery)`.      

*Called by*:    
`dhcp.py` -> `Transaction` -> `receive(self, packet)`  

*Return*: None      

| Type | Variable | Description |
|-------|-------|-------|
| ReadBootProtocolPacket | discovery | Object that contains the MAC address, requested IP address, device's host name or '', and the timestamp |

Related Classes and functions: [DHCPServerConfiguration](###DHCPServerConfiguration)     

#### Function: send_offer(self, discovery)
*Description*:   
Uses the WriteBootProtocolPacket object to create an offer with the current DHCPServerConfiguration properties. The `parameter_order` instance variable in the packet will have the same value as `parameter_request_list` in `options` of `listener.py`. All the instance variables from WriteBootProtocolPacket will be filled out and have the message type set as DHCPOFFER. After all values have been written, the `DHCPServer` will broadcast (`DHCPServer.broadcast(self, packet)`) the offer.        

*Called by*:    
`dhcp.py` -> `Transaction` -> `received_dhcp_discover(self, discovery)`  

*Return*: None         

| Type | Variable | Description |
|-------|-------|-------|
| ReadBootProtocolPacket | discovery | Object that contains the MAC address, requested IP address, device's host name or '', and the timestamp |

Related Classes and functions: [WriteBootProtocolPacket](###WriteBootProtocolPacket)          

#### Function: received_dhcp_request(self, request)
*Description*:   
Will replace the current line with the MAC address with the new IP address using `DHCPServer.client_has_chosen(self, request)`and will send an DHCPACK in return then call `Transaction.close(self)`.

*Called by*:    
`dhcp.py` -> `Transaction` -> `receive(self, packet)`    

*Return*: None      

| Type | Variable | Description |
|-------|-------|-------|
| ReadBootProtocolPacket | discovery | Object that contains the MAC address, requested IP address, device's host name or '', and the timestamp |

Related Classes and functions: [DHCPServer.broadcast(self, offer)](###DHCPServer), [WriteBootProtocolPacket](###WriteBootProtocolPacket), [HostDatabase] (###HostDatabase)     

#### Function: acknowledge(self, request)
*Description*:   
Broadcast with `DHCPServer.broadcast(self, offer)` an DHCPACK with `WriteBootProtocolPacket` and setting all the correct parameters. Checkout `listener.py` and `WriteBootProtocolPacket` to see other attributes.

*Called by*:    
`dhcp.py` -> `Transaction` -> `send_offer(self, request)`  

*Return*: None      

| Type | Variable | Description |
|-------|-------|-------|
| ReadBootProtocolPacket | discovery | Object that contains the MAC address, requested IP address, device's host name or '', and the timestamp |

Related Classes and functions: [DHCPServer.broadcast(self, offer)](###DHCPServer), [WriteBootProtocolPacket](###WriteBootProtocolPacket)          

#### Function: received_dhcp_inform(self, inform)
*Description*:   
Closes current Transaction by calling `Transaction.close(self)` and replaces IP address to the MAC address in `hosts.csv` by calling `DHCPServer.client_has_chosen(self, packet)`.      

*Called by*:    
`dhcp.py` -> `Transaction` -> `receive(self, packet)`    

*Return*: None      

| Type | Variable | Description |
|-------|-------|-------|
| ReadBootProtocolPacket | discovery | Object that contains the MAC address, requested IP address, device's host name or '', and the timestamp |

Related Classes and functions:  [DHCPServer.broadcast(self, offer)](###DHCPServer), [WriteBootProtocolPacket](###WriteBootProtocolPacket), [HostDatabase] (###HostDatabase)             

---
### **CSVDatabase**
#### Function: __init__(self, file_name)
*Description*:     
Initializes the database for the manually inputted MAC addresses from the `hosts.csv`. If the file does not exist, this will create the `hosts.csv` file. Look into Python's `open()` function for more information.      

*Called by*:    
`dhcp.py` -> `HostDatabase` -> `__init__`  

*Return*: None          

| Type | Variable | Description |
|-------|-------|-------|
| String | file_name | File name of the database (note that it has the extension in the name) |


#### Function: file(self, mode = 'r')
*Description*:     
Will open the file in reading mode as default, unless specified otherwise         

*Called by*:    
`dhcp.py` -> `CSVDatabase` -> `__init__`       
`dhcp.py` -> `CSVDatabase` -> `all(self, pattern)`       
`dhcp.py` -> `CSVDatabase` -> `add(self, line)`       
`dhcp.py` -> `CSVDatabase` -> `delete(self, pattern)`       

*Return*: (File Object) for `hosts.csv` (this can be called the file handler as well)              

| Type | Variable | Description |
|-------|-------|-------|
| String | mode | Description of the mode for file (options: 'r', 'w', 'x', 'a', 't', 'b', '+') |

Related Classes and functions: [CSVDatabase](###CSVDatabase), [HostDatabase.get()](###HostDatabase)    


#### Function: get(self, pattern)
*Description*:     
Get the specified MAC address or IP address             

*Called by*:    
`dhcp.py` -> `HostDatabase` -> `get(self, **kw)`             

*Return*: (String) line from `hosts.csv` that contains a specified pattern               

| Type | Variable | Description |
|-------|-------|-------|
| List | pattern | Pattern from Host.get_pattern function |

Related Classes and functions: [CSVDatabase](###CSVDatabase), [HostDatabase.get()](###HostDatabase), Host.from_tuple(cls, line), Host.from_packet(cls, packet), [DHCPServer.get_ip_address(self, packet)](DHCPServer)    


#### Function: add(self, line)
*Description*:     
Open the file and appends new values in `hosts.csv` in format shown at [Why dhcp.py is designed like this?](). Keep in mind, in the beginning we said we must manually add these values. This function is only used for replace what is already there in the `hosts.csv`.         

*Called by*:    
`dhcp.py` -> `HostDatabase` -> `add(self, host)`         

*Return*: None              

| Type | Variable | Description |
|-------|-------|-------|
| List | line | list of String values |

Related Classes and functions: [CSVDatabase](###CSVDatabase), [HostDatabase.add()]()    
      
#### Function: delete(self, pattern)
*Description*:   
Removes specified pattern (MAC address) from the `hosts.csv` by rewriting the file with the new values

*Called by*:    
`dhcp.py` -> `HostDatabase` -> `delete(self, host = None, **kw)`    

*Return*: None         

| Type | Variable | Description |
|-------|-------|-------|
| String | pattern | pattern of MAC address to delete |
        
Related Classes and functions: [CSVDatabase](###CSVDatabase), [HostDatabase.delete()]()    

#### Function: all(self)
*Description*:   
Gets all the values from `hosts.csv` into a list

*Called by*:    
`dhcp.py` -> `HostDatabase` -> `all(self)`    

*Return*: (List) All MAC addresses in the format as shown earlier in documentation as a list         
        
Related Classes and functions: [CSVDatabase](###CSVDatabase), [HostDatabase.all()](###HostDatabase)    

---
### **HostDatabase** 
#### Function: __init__(self, file_name)
*Description*:     
Initializes the database for the manually inputted MAC addresses from the `hosts.csv` with `CSVDatabase`. If the file does not exist, this will create the `hosts.csv` file by calling `CSVDatabase`. Look into Python's `open()` function for more information.      

*Called by*:    
`dhcp.py` -> `DHCPServer` -> `__init__(configuration = None)`  

*Return*: None          

| Type | Variable | Description |
|-------|-------|-------|
| String | file_name | File name of the database (note that it has the extension in the name) |


#### Function: get(self, **kw)
*Description*:     
Get the specified MAC address or IP address       

*Called by*:    
`dhcp.py` -> `HostDatabase` -> `get(self, **kw)`             

*Return*: (String) line from `hosts.csv` that contains a specified pattern               

| Type | Variable | Description |
|-------|-------|-------|
| Function | **kw | Pattern from Host.get_pattern function |

Related Classes and functions: [CSVDatabase](###CSVDatabase), [HostDatabase.get()](###HostDatabase), Host.from_tuple(cls, line), Host.from_packet(cls, packet), [DHCPServer.get_ip_address(self, packet)](###DHCPServer)    


#### Function: add(self, host)
*Description*:     
Open the file and appends new values in `hosts.csv` in format shown at [Why dhcp.py is designed like this?]() by calling CSVDatabase.add(line). Keep in mind, in the beginning we said we must manually add these values. This function is only used for replace what is already there in the `hosts.csv`.             

*Called by*:    
None    

*Return*: None              

| Type | Variable | Description |
|-------|-------|-------|
| List | line | list of String values |

Related Classes and functions: [CSVDatabase](###CSVDatabase)  
      
#### Function: delete(self, pattern)
*Description*:   
Removes specified pattern (MAC address) from the `hosts.csv` by rewriting the file with the new values

*Called by*:    
`dhcp.py` -> `HostDatabase` -> `replace(self, host)`         

*Return*: None         

| Type | Variable | Description |
|-------|-------|-------|
| String | pattern | pattern of MAC address to delete |
        
Related Classes and functions: [CSVDatabase](###CSVDatabase)    

#### Function: all(self)
*Description*:   
Gets all the values from `hosts.csv` into a list

*Called by*:    
`dhcp.py` -> `HostDatabase` -> `replace(self, host)`    

*Return*: (List) All MAC addresses in the format as shown earlier in documentation as a list         
        
Related Classes and functions: [CSVDatabase](###CSVDatabase), [HostDatabase.all()](###HostDatabase)    

#### Function: replace(self, host)
*Description*:   
Gets all the values from `hosts.csv` into a list

*Called by*:    
`dhcp.py` -> `DHCPServer` -> `client_has_chosen(self, packet)`     
`dhcp.py` -> `DHCPServer` -> `get_ip_address(self, packet)`    

*Return*: None               
        
Related Classes and functions: [DHCPServer](###DHCPServer)  

---
### **DHCPServerConfiguration**
#### Function: __init__(self, ip, subnet_mask)
*Description*:   
Initialize values with the given IP address

*Called by*:    
`dhcp.py` -> `DHCPServer` -> `__init__(self, configuration)`    
`dhcp.py` -> `do_dhcp(ip, subnet_mask, mac_ip_file)`  

*Return*: None      

| Type | Variable | Description |
|-------|-------|-------|
| String | ip | IP address in string format |
| String | subnet_mask | Subnet Mask value in string format |

Related Classes and functions: [DHCPServer](###DHCPServer), [do_dhcp(ip, subnet_mask, mac_ip_file)](####Function:-do_dhcp(ip,-subnet_mask,-mac_ip_file)))    

#### Function: load(self, file)
*Description*:   
Reads the `hosts.csv` file and saves into a private instance dictionary value

*Called by*: None      

*Return*: None      

| Type | Variable | Description |
|-------|-------|-------|
| String | file | Name of the file with the extension |


#### Function: all_ip_addresses(self)
*Description*:   
Returns ip addresses available with the current network address and subnet mask

*Called by*:    
`dhcp.py` -> `do_dhcp(ip, subbnet_mask, mac_ip_file)`   
`dhcp.py` -> `DHCPServer` -> `DHCPServer.get_ip_addresses(self, packet)`     

*Return*: (Iterator) String of IP addresses      

Related Classes and functions: [DHCPServer](###DHCPServer), NETWORK    

#### Function: network_filter(self)
*Description*:   
Creates NETWORK object for comparisons of IP addresses

*Called by*:    
`dhcp.py` -> `DHCPServer` -> `DHCPServer.get_ip_addresses(self, packet)`       

*Return*: (NETWORK) Object      

Related Classes and functions: [DHCPServer](###DHCPServer)         

---
### **DHCPServer**   
#### Function: __init__(self, configuration)
*Description*:   
Initializes with the set up configuration. DHCPServer declares the socket to use UDP with `socket(type = SOCK_DGRAM)` and binds to port 67 (keep in mind it binds to all so you may end up getting other people's vlan's and other addresses). This sets up the broadcast socket on port 67 as well initializing the creation of Transaction object and DelayWorker object.

*Called by*:    
`dhcp.py` -> `do_dhcp(ip, subnet_mask, mac_ip_file)`     

*Return*: None      

| Type | Variable | Description |
|-------|-------|-------|
| DHCPServerConfiguration | configuration | Configurations set by DHCPServerConifugration object |

Related Classes and functions: [Transaction](###Transaction), [DelayWorker](###DelayWorker), [HostDatabase](###HostDatabase), [CSVDatabase](###CSVDatabase)    

#### Function: close(self)
*Description*:   
Closes the Delay Worker object as well as Transaction

*Called by*:    
`dhcp.py` -> `DHCPServer` -> `run()`  

*Return*: (Type) Description of object      

Related Classes and functions: [Transaction](###Transaction), [DelayWorker](###DelayWorker), [HostDatabase](###HostDatabase), [CSVDatabase](###CSVDatabase)        

#### Function: update(self, timeout)
*Description*:   
Depending on the transaction id (client id) it'll receive the packet by using ReadBootProtocolPacket and will close the Transaction object if all files are done transferring and pop it from the Transactions dictionary. Checkout socket.settimeout in the Python API to understand what timeout is for.

*Called by*:    
`dhcp.py` -> `DHCPServer` -> `run()`  

*Return*: None           

| Type | Variable | Description |
|-------|-------|-------|
| Integer | timeout | The amount of time spent listening for packets |

Related Classes and functions: [Transaction](###Transaction)        

#### Function: received(self, packet)
*Description*:   
Used for debugging to see if the server receieved a different message type from Transaction not listed in Transaction.receive(self, packet)

*Called by*:    
None     

*Return*: None      

| Type | Variable | Description |
|-------|-------|-------|
| ReadBootProtocolPacket | packet | Object that contains the MAC address, requested IP address, device's host name or '', and the timestamp  |   

Related Classes and functions: [Transaction](###Transaction)       

#### Function: client_has_chosen(self, packet)
*Description*:   
Replaces IP address from `hosts.csv` if the client has requested a valid ip address

*Called by*:    
`dhcp.py` -> `Transaction` -> `send_offer(self, discovery)`  

*Return*: None      

| Type | Variable | Description |
|-------|-------|-------|
| ReadBootProtocolPacket | packet | Object that contains the MAC address, requested IP address, device's host name or '', and the timestamp  |   

Related Classes and functions: Host       

#### Function: is_valid_client_address(self, address)
*Description*:   
Checks if the given address is a valid IP client address

*Called by*:    
`dhcp.py` -> `DHCPServer` -> `get_ip_address()`  

*Return*: (Boolean) True if address is valid else False       

| Type | Variable | Description |
|-------|-------|-------|
| String | address | IP Address in String format with '.' as delimiters |

Related Classes and functions: [DHCPServerConfiguration](###DHCPServerConfiguration)   

#### Function: get_ip_address(self, packet)
*Description*:   
Selects an IP address after receiving a packet. If the MAC address is known from the `hosts.csv`, the IP address from the file will be given. If the IP address does not exist in the file, however, the request IP address is valid, then the IP address given will be the requested ip from the RPi. If there is no IP requested, then the server will assign a valid IP address of its choosing; however, if all available IP addresses were taken then it'll reuse and old valid IP address. At the last if-statement it'll replace the empty IP addresses that was manually entered and assign it a new IP address from the above options.

*Called by*:    
`dhcp.py` -> `Transaction` -> `send_offer(self, discovery)`    
`dhcp.py` -> `Transaction` -> `acknowledge(self, discovery)`    

*Return*: (String) IP address      

| Type | Variable | Description |
|-------|-------|-------|
| Type | packet | Description of the argument and what it is |

Related Classes and functions: [DHCPServer.received(self, packet)](###DHCPServer), [DHCPServer.update(self, timeout)](###DHCPServer)    

#### Function: broadcast(self, packet)
*Description*:   
Send

*Called by*:    
`dhcp.py` -> `Transaction` -> `send_offer(request)`      
`dhcp.py` -> `Transaction` -> `acknowledge(request)`     

*Return*: None        

| Type | Variable | Description |
|-------|-------|-------|
| ReadBootProtocolPacket | packet | String format of the ReadBootProtocolPacket translated from the bytes in received (Object that contains the MAC address, requested IP address, device's host name or '', and the timestamp) |

Related Classes and functions: [WriteBootProtocolPacket.options](###WriteBootProtocolPacket), [DHCPServer.update(self, timeout)](###DHCPServer)    

#### Function: run(self)
*Description*:   
Continuously listens and updates until there is a KeyboardInterrupt

*Called by*:    
`dhcp.py` -> `do_dhcp(ip, subnet_mask, mac_ip_file)` 

*Return*: None      

Related Classes and functions: [Transaction](###Transaction)         


---
## Additional Notes and Citations
---
The following words here cite where the DHCP library and *WriteBootPacket* comes from when used in the DHCP. This library takes care of writing the DHCP packet and formating.
#### Python DHCP Server Library   
[Download](https://github.com/niccokunzmann/python_dhcp_server/releases)

This is a purely Python DHCP server that does not require any additional libraries or installs other that Python 3.

It was testet under Ubuntu 14 with Python and Windows 7. It does not use any operating system specific Python functions, so it should work when Python 3 works.

dhcpgui lists MAC address, IP address and host name.

This DHCP server program will assign IP addresses ten seconds after it received packets from clients. So it can be used in networks that already have a dhcp server running.

Contributions welcome!

#### Related Work
- [Adafruit-Pi-Finder](https://github.com/adafruit/Adafruit-Pi-Finder) - finde deinen Raspberry Pi im Netzwerk
