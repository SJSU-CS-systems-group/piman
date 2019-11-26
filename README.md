# **Raspberry Pi Manager** 
This repository will contain the project work done by the members of Team Budapest throughout the course of the Fall 2019 semester in CS158B. Throughout the documentation, there will be files and folders referenced, but they will be referred to as if you are currently located in the ***root*** directory of this repository.     
Note: The original notes left behind by the originator, Team Ice from Fall 2018, will be kept as documentation and has been moved to [Additional Notes](##Additional-Notes) because documentation is important.      

## **Table of Contents**      
[Purpose and Background](##Purpose-and-Background)   
[Issues](##Issues)   
[Setting Up Your Environment](##Setting-Up-Your-Environment)   
[Quick-Start Guide](##Quick-Start-Guide)
[.env](##env)
[config.py](##config.py)   
[config.ini](##config.ini)   
[piman.py](##piman.py)   
[Utility](##Utility)   
1) [findport.py](###findport.py)       
2) [power_cycle.py](###power_cycle.py)          

[DHCP](##DHCP)    
[TFTP](##TFTP)  
[TCP](##TCP)   
[hello_protocol.sh](##hello_protocol.sh)   
[make_zippapp.sh](##make_zippapp.sh)   
[Monitoring](##Monitoring)   
[Additional Notes](##Additional-Notes)   


## **Purpose and Background**      
The purpose of this project is to experience monitoring and managing devices on a network. Students will be working on pre-existing code to simulate a real work environment in the industry where you do not start from scratch. The project will be split into three phases: debugging the code, monitoring the Raspberry Pi's, and TBD. At the end of phase 1, students should be able to network boot all of their assigned pi's. At phase 2, students will be monitoring their Raspberry Pi's as your supervisor will wreak havoc with unknown fury upon your Raspberry Pi's and you will have to write a post-mortem report and an incident report as you monitor your servers and devices. Have fun. :)   
     
## **Quick-Start Guide**    
---
This section will explain the general flow of this code.    
Preconditions:     
Before you start running your server, you'll have to create and move some files by executing a few scripts. You must execute `install/initram/create_initramfs.gz.sh` to zip `install/initram/hello_protocol.sh` and `install/initram/init` into the `install/boot` directory. Otherwise, the pi has no way to communicate with you via TCP server later on. Then, after you create those files, you may execute `make_zipapp.sh` to create a packaged zipped-files (that contains all your dependencies) in order to run your Pi Manager program continuously via **service file** and become acquainted with the command `systemctl`.    
Explanation:     
You should look and change the configurations in the `.env` file and the `config.py` so you know what values are being handed to the program. After you understand what these files do and have set the proper values, you may proceed to look at the `piman.py`. The `piman.py` creates three threads when you start the server, one to start the DHCP server, one to start the TFTP server, and one to start TCP to transfer the bigger files (read more about the `piman.py` later in this section). After you start `piman.py`, you'll see all the messages in the console, printing from the three different threads - go check out where all the messages are printing from so you have the general gist of what's going on and where all the threads are waiting at what function. After the threads have started, open up another console and *restart* a single a pi - you should see the DHCP and the pi interacting with one another in the console with DHCPDISCOVERY, DHCPREQUEST, and DHCPOFFER (Read `dhcp/README.md` for more details). After the DHCP has assigned a valid IP address to the pi, TFTP will begin to send over the boot files from the `install/boot` directory to the Pi with UDP (Read `tftp/README.md`). After TFTP has sent over all the files from `install/boot` directory, TCP will begin to install your pi by sending over the `install/boot/rootfs.tgz` and then communicating with Pi to see if the rootfs.tgz has installed (checkout `/install/initram/README.md` and `tcp/README.md` to learn more about how these two communicate to install the Pi). After it has successfully installed, you should be able to ping the Pi `ping <Pi's IP address>` or SSH into Pi `ssh pi@<Pi's IP address>` (ask your supervisor for the password).     
**Note: If you are reinstalling your Pi's, please reset the `reinstall.txt` file or else it'll reinstall the same Raspberry Pi like how piman was called last time with restart!**    

## **Issues**    
---
## Some Recommendations   
We recommend you try to run through the code and to see the different parts of the code. Please make sure you ***START EARLY (not the week before it's due)*** on this project because there will be hardware issues that are not easily diagnosed and this may prove to be difficult to grasp what the code is doing... even with documentation. We will try to improve the clarity with our documentation, but we cannot guarantee such promises. Apologies.    

## Phase 1 and 2   
Port 1, 2, 3, 4, 5, and 6 all boot properly
Ephemeral ports also led to a side problem that could be a simple fix, but we couldn't figure out the issue. (see Non-Piman notes #6)     

## **Setting Up Your Environment**
---
Before you even think of executing or testing the program, make sure you have your dependencies installed. The `make_zipapp.sh` creates the dependencies for you in the `build/` directory; however, if you're just running the `piman.py` you'll have to install a few things. We are assuming that python 3.7 < higher is installed. Be careful what version you install your dependencies, because Linux virtual machines tend to have both python2 and python3. Here are the commands you should execute in sequential order:        
What to do:    
```bash
sudo apt-get install python3-pip 
pip install click 
pip install pysnmp
pip install python-dotenv
```
What to NOT do:   
```bash
sudo apt-get install python-pip # This installs for python2
pip install click # fortunately these dependencies don't have a specific version tagged to it, but make sure to check because we're not time travelers :( boohoo
pip install pysnmp
pip install python-dotenv
```
    
   

## **config.ini**
---
The following file is the only file you will need to update (no need to update the code files)
The files contains:
Section [hardcoded]
and Options
[ip, router, switchAddress, reinstall]
These values should be changed to the appropriate value for your group. The code files will retrieve the variables and values from this document.

## **config.py**
The following module has the method to help other modules read the value in config.ini.    

## **piman.py**
---
### What is piman.py?

`piman.py` is a DHCP server that runs on a virtual network on Prof. Ben's cs-reed-03.cs.sjsu.edu machine.  
Its purpose is to simulate a SNMP manager for a set of Raspberry Pi's on the virtual network.  

Functionalities include:  

* Running the piman server in the background
```bash
sudo python3 piman.py server &
```
* Restarting a raspberry pi
```bash
sudo python3 piman.py restart <port number of a pi>
```
* Reinstalling a raspberry pi
```bash
sudo python3 piman.py reinstall <port number of a pi>
```

### Why piman.py?

`piman.py` exists to be the process that enables network booting and communication with raspberry pi's over the virtual network.  
This is neccessary because the pi's are being hosted on a virtual network on Ben's virtual machine.  
To do this `piman.py` is designed to use DHCP, TCP, and TFTP protocols to give the pi's ip addresses, connect to them, and transfer boot files to them.  
These protocols need to be active in order to communicate with the pi's remotely, which is why `piman.py` is implemented as a server.  

### How does it work?

Before actually performing any functions, `piman.py` will gather some parameters from a configuration file called `config.py`:  
```python
ip = config.PI_NET_ADDR
data_dir = "./install/boot"
tftp_port = int(config.TFTP_PORT)
tcp_port = int(config.TCP_PORT)
subnet_mask = config.SUBNET
mac_ip_file = "hosts.csv"
```
For more information, see the README for `config.py`.  

### There are 3 functions that exist to implement the functionalities described in the "what is piman" header.

#### Running the server
```python
def server(): 
    tftp_thread = Thread(target=tftp.do_tftpd, args=[data_dir, ip, tftp_port], name="tftpd")
    tftp_thread.start()

    dhcp_thread = Thread(target=dhcp.do_dhcp, args=[ip, subnet_mask, mac_ip_file], name="dhcpd")
    dhcp_thread.start()

    tcp_thread = Thread(target=tcp.do_tcp, args=[data_dir, tcp_port, ip], name="tcp")
    tcp_thread.start()

    tftp_thread.join()
    dhcp_thread.join()
    tcp_thread.join()
```
This function will initiate threads for each of the DHCP, TCP, and TFTP protocols.  
The '&' will ensure that the threads will run in the background.  
This function should be called 1st because network booting relies on these protocols.    
For more information about the implementation of the protocols, see their respective READMEs.  

  
#### Restarting a raspberry pi  
```python
def restart(ports):
    for port in ports:
        power_cycle.power_cycle(port)
```
This function will turn the pi on the specified port off and then on.  
Although the implementation makes it seem like you can restart multiple pi's at once, it is recommended to restart them 1 at a time.  
`/utility/power_cycle.py` is used to turn the pi off or on. For more imformation of `power_cycle.py`, see its README.  

  
#### Reinstalling a raspberry pi
```python
def reinstall(port):
    ip_range = str(ip)
    ip_range = ".".join(ip_range.split('.')[0:-1]) + '.'
    with open("reinstall.txt", "w") as f:
        f.write(ip_range + "{}".format(port))
    power_cycle.power_cycle(port)
```
This function will reinstall the pi on the specified port.  
The reinstallation process uses `/utility/power_cycle.py` to turn the pi at the port off and then on before attempting to perform a  
network boot to install the pi.  
To perform a network boot, the DHCP, TCP, and TFTP threads should be running.  

  
#### There is a 4th function to handle input errors on the command line on the terminal
```python
def exit_piman():
    print("Insufficient amount of arguments")
    exit(1)
```
The input errors that are to be detected are described in __main__
```python
if len(argv) < 2:
        power_cycle.power_cycle(10)
        server()
        exit()

    if argv[1] == "server":
        server()
    elif argv[1] == "restart":
        if len(argv) < 3:
            exit_piman()
        restart(argv[2])
    elif argv[1] == "reinstall":
        if len(argv) < 3:
            exit_piman()
        reinstall(argv[2])
    else: 
        power_cycle.power_cycle(10)
        server()
```    

## **Utility**
---
### findport.py    
### What is find_port.py?

`find_port.py` is a script that will search the network for the port that a raspberry pi is on.

### Why find_port.py?

Because the pi's are hosted on a virtual machine, find_port.py is a useful tool to remotely fetch the port that a pi is on.  
To do this, `find_port.py` is designed to take in the MAC address of the target pi, the ip address of the switch, and the VLAN address of the virtual network.  
`find_port.py` will use the SNMP protocol to look for the port that contains a device with the given MAC address.  
#### It is important to note that this implementation will be accessing a sysDesrc object using an OID, there is a chance that the output will not produce the port that the pi should be on due to an error in the pi's configuration. In that case, ask Prof. Ben.

### How does it work?

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
   
### power_cycle.py     
### What is power_cycle.py?

`power_cycle.py` is a script that will turn the raspberry pi at a specified port off and then on.  
`power_cycle.py` is used by the restart and reinstall functions defined in `/../piman.py`  

### Why power_cycle.py?

`power_cycle.py` is needed to turn the raspberry pi's off and on remotely.  
To do this, `power_cycle.py` is designed to use the SNMP protocol to change an OID value in the MIB which will trigger a command to  
turn the pi's.  
When calling restart from `/../piman.py`, the pi will simply turn off and on.  
When calling reinstall from `/../piman.py`, the pi will try to network boot after turning off and on.  

### How does it work?

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


## **DHCP**
---
Navigate to `dhcp/README.md` to read about DHCP.    

## **TFTP**    
---
Navigate to `tftp/README.md` to read about TFTP.    

## **TCP**   
---   
Navigate to `tcp/README.md` to read about TCP. **Note: to reinstall, please reset the `reinstall.txt` file or else it'll reinstall the same Raspberry Pi like how piman was called last time with restart!**    

## **hello_protocol.sh**   
---   
Navigate to `install/initram/README.md` to read about hello_protocol.sh.    

## **make_zippapp.sh**   
---
### What is make_zipapp.sh?

make_zipapp.sh is a script that will compress the entire repository into a /build directory.

### Why make_zipapp.sh?

make_zipapp.sh will generate a build directory with a piman.pyz that should be run to manage the network.  
This method of running the program was chosen because in all dependencies in the code will be present in the generated /build directory.  

### How does it work?

The 1st thing the script will do is delete any existing /build directory before creating a fresh ./build directory.  
```bash
#!/bin/bash
rm -rf build
mkdir build
```
Afterwards the script will install pysnmp (a dependency) and move all of the dependencies into /build
```bash
PYTHONUSERBASE=$PWD/build python3 -m pip install click pysnmp python-dotenv --no-warn-script-location
mkdir build/piman.app
(
    cd build/lib/python*/site-packages
    mv $(ls | grep -v -) ../../../piman.app
)
```
Then the script will copy the protocol python files and utility python files into the /build directory
```bash
cp -r utility tftp dhcp monitoring tcp *.py build/piman.app
```
Then the script will create a /build/install directory and move boot files into it
```bash
mkdir build/piman.app/install
cp -r install/boot build/piman.app/install
```
The script will also remove all of the crytpo from /build
```bash
rm -r build/piman.app/Crypto*
```
Finally, the script will generate the pyz file using zipapp
```bash
python3 -m zipapp build/piman.app
```
See [https://docs.python.org/3/library/zipapp.html] for more information about zipapp    
  

## **Monitoring**    
---
### Manager (Needs to be updated later ...)

There is a monitoring client running on the manager pi the periodically sends a get request to each node. The monitoring server running on the nodes respond with current status. To install the dependencies and run the client, run the following commands from the root directoyry of `pi-manager-ice`:

```sh
python3 -m pip install requests

# run server and redirect standard out to a log file
python3 monitoring/monitoring-client.py <path_to_config> > logs/status.log
```

### Nodes
Each node pi (2-10) runs it's own custom made monitoring servers using Python 3 and Flask. The server currently supports one `GET` API endoint:

- [http://172.30.3.<pi_number>:3000/events](http://172.30.3.<pi_number>:3000/events) - This get request gives a response with the following information as JSON:

    | Key            | Value                      |
    |----------------|----------------------------|
    | time           | Current Timestamp          |
    | cpu_percent    | The CPU usage              |
    | memory_percent | The RAM usage              |
    | disk_percent   | The Disk usage             |
    | num_pids       | Number of active processes |


To get the server running, move over the `./monitoring` directory to each of the pi nodes and install the dependencies and run the server:

```sh
python3 -m pip install flask-restful
python3 -m pip install psutil
    
# run the server
python3 monitoring_server.py
```

### Configuration and Alerts    
To customize the timeout between each system check and/or the thresholds to alert, you can edit the `monitoring/monitoring.config`. 


Currently the system send a slack message to `#ice2` channel. You can create a slack app and set up webhooks to link your channel to the system. Follow [this](https://get.slack.help/hc/en-us/articles/115005265063-Incoming-WebHooks-for-Slack) slack tutorial.


### Start Up Scripts   
The `/etc/rc.local` file has been updated on the manager and the nodes to run the server and monitoring tools from startup. Take a look at it for each machine to get a better understanding of the startup process. 


## **Additional Notes**   
---
### Non-Piman notes
At the time we wrote this, we only have 6 pi's. Therefore, when specifying a pi, please be sure to only use ports 1-6.
The following steps need to be followed in order.

*    1) run make_zipapp.sh (this will create a build directory that will also have the python.pyz file in it)

*    2) run sudo python3 piman.py server & (this will run the TFTP, DHCP, and TCP threads in the background)

*    3) run sudo python3 piman.py reinstall (pi port) (this will restart your pi and reinstall it)

*    3.5) If this is the first time running reinstall, then you will not have a hosts.csv file. Running it once will create a hosts.csv file for you.
        This file needs to be updated so that any known mac addresses can successfully make a DHCP request and get an offer (all unknown mac addresses will be declined an offer)
        
*    4) sudo vi hosts.csv (this is a read only file, so you need sudo to update it)
        within hosts.csv, write the following for each pi you have
        
        MAC_ADDRESS;0.0.0.0;;(any number)
        
        Ex:
        
        B8:27:EB:11:B7:41;0.0.0.0;;0
        
        B8:27:EB:E2:E1:32;0.0.0.0;;0
        
        (add lines for the rest of your pi's)
        
*    5) rerun steps 2-3.

*    6) Each time you run reinstall / restart, you will need to restart the server. (This is the side problem introduced when adding ephemeral ports)

*    7) To make sure the systemd service file is working, type "systemctl start piman.service" then "systemctl status piman.service" after. To access the file, it is under /usr/lib/systemd/system.
        You may want to update the directory path of piman.py under ExecStart if you make changes to piman.py.
    
* To test if a pi successfully booted up, ping the ip address it was assigned. Alternatively, ssh into that ip_address.
---


### Piman (Updated Notes)
Piman has multiple functionalities.

* Server - to run the piman server in the background, 
    sudo python3 piman.py server &
    
* Restart - To restart a pi, run the following command
    sudo python3 piman.py restart (port of pi you want to restart)
    Ex: sudo python3 piman.py restart 2
    
* Reinstall - To reinstall a pi, run the following command
    sudo python3 piman.py reinstall (port of the pi you want to reinstall
    Ex: sudo python3 piman.py reinstall 1


### DHCP Server

The DHCP server utilized for this project is a very lightweight, barebone version of [this DHCP server](https://github.com/niccokunzmann/python_dhcp_server). To manually assign IPs to known MAC addresses, you can modify the `hosts.csv` file located in the root of the main directory. The Pis will send a DHCP packet to the manager which in then responds with an IP and the location of the TFTP server. 

### TFTP Server

The TFTP server is responsible for serving the boot files needed for each node to start-up correctly. The TFTP code is pretty straightforward, but here's somethings to look out for: 

* The TFTP server serves files from `install/boot` directory
* **You must put `rootfs.tgz` inside this directory** 
* You can edit `hello_protocol.sh` located in `install/initram` directory. **Be sure to run `install/initram/create_initramfs.gz` to create the `initramfs.gz `**. Please note that `create_initramfs.gz` has been updated to place the created zip in the `install/boot` directory. 

### TCP Server

The server side of Hello Protocol is implemented here.    