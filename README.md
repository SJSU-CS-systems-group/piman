# **Raspberry Pi Manager (Piman) / Raspberry Pi Network Management Software** 
This repository will contain the project work done by the members of Team Budapest throughout the course of the Fall 2019 semester in CS158B. Throughout the documentation, there will be files and folders referenced, but they will be referred to as if you are currently located in the ***root*** directory of this repository.     
Note: The original notes left behind by the originator, Team Ice from Fall 2018, will be kept as documentation and has been moved to [Additional Notes](##Additional-Notes) because documentation is important, or has been moved to the appropriate sections through this README.      

## **Table of Contents**      
[Purpose and Background](##Purpose-and-Background)   
[Issues](##Issues)   
[A Note To Our Readers](##A-Note-To-Our-Readers...)
[Set Up Your Configurations](##Set-up-your-configurations)   
[Quick-Start Guide](##Quick-Start-Guide)  
[piman.py](##piman.py)   
[Utility](##Utility)   
1) [findport.py](###findport.py)       
2) [power_cycle.py](###power_cycle.py)   

[About the OID...](##About-the-OID...)
[DHCP](##DHCP)    
[TFTP](##TFTP)  
[TCP](##TCP)   
[hello_protocol.sh](##hello_protocol.sh)   
[make_zippapp.sh](##make_zippapp.sh)   
[Monitoring](##Monitoring)   
[Configuration and Alerts](##Configuration-and-Alerts)
[Grafana Dashboard](##Grafana-Dashboard)    
[Logs](##Logs)   
[NTP Server](##NTP-Server)   
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

## **A Note to Our Readers...**
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
## **Set up your configuration**
---
### Configuration UI

Included in PiMan is a user-interface designed to allow easier setup of configuration and pis.  Use the piman config launch option shown above.  Navigate to the webserver, hosted on port 5000.  If you are accessing the webserver from the same machine, you can use localhost:5000 in any browser.  Click on 'CONFIG' to generate the configuration file and begin configuration.  Click on 'HOSTS.CSV' to generate the hosts file and begin configuration for that.  Remember to click the apply changes button before navigating to a different page.  Once you are done applying changes, restart piman manually for those changes to take effect.

By default, the webserver will modify the files .yaml and hosts.csv in the root directory of PiMan.

If PiMan is hosted on a VM and you'd like to access the configuration UI from a different client, you can use 'ssh -N -L 5000:localhost:5000 name@city'.  Replace name@city to be the VM login that you would like to link to.  You should now be able to connect to the webserver by going to 'localhost:5000' in your browser.

### Config Format

If you would like to configure PiMan manually instead of using the UI, follow this format.  To configure piman, create a YAML file with the following format:

```
private_number:
server_address:
subnet_mask:
interface: 
switch_count:
switches:
  - swtich_0_address:
    pi_addresses:
      -
      -
      -
  - swtich_1_address:
    pi_addresses:
      -
      -
  .
  .
  . 
```

For example:
```
private_number: 4
server_address: 172.30.4.1
subnet_mask: 255.255.255.0
interface: ens4
switch_count: 2
switches:
  - swtich_0_address: 172.30.4.254
    pi_addresses:
      - 172.30.4.13
      - 172.30.4.14
      - 172.30.4.15
      - 172.30.4.16
      - 172.30.4.17
      - 172.30.4.18
      - 172.30.4.19
      - 172.30.4.20
  - swtich_1_address: 172.30.4.128
    pi_addresses:
      - 172.30.4.1
      - 172.30.4.2
      - 172.30.4.3
      - 172.30.4.4
      - 172.30.4.5
      - 172.30.4.6
```

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
    `python3 piman.py restart <switch number> [list of pi_numbers]`

    `python3 piman.py restart 172.30.4.254 2 3 4` -> restarts pi 2, 3, and 4 for the switch 172.30.4.254 
    `python3 piman.py reinstall <switch number> [pi_number]`

### There are 4 functions that exist to implement the functionalities described in the "what is piman" header.

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
  
#### Restarting a raspberry pi  
```python
def restart(switch_address, ports):
    for port in ports:
        power_cycle.power_cycle(switch_address, port)
```
This function will turn the pi on the specified port off and then on.  
Although the implementation makes it seem like you can restart multiple pi's at once, it is recommended to restart them 1 at a time.  
`utility/power_cycle.py` is used to turn the pi off or on. For more imformation of `power_cycle.py`, see its README.  

  
#### Reinstalling a raspberry pi
```python
def reinstall(switch_address, port):
    with open("/tcp/reinstall.txt", "w") as f:
        network_addr = ip[:-1]
        f.write(network_addr+str(port))
    power_cycle.power_cycle(switch_address, port)
```
This function will reinstall the pi on the specified port.  
The reinstallation process uses `/utility/power_cycle.py` to turn the pi at the port off and then on before attempting to perform a  
network boot to install the pi.  
To perform a network boot, the DHCP, TCP, and TFTP threads should be running.  

  
#### There is a 4th function to handle input errors on the command line on the terminal
```python
def exit_piman():
    logger.error("Insufficient amount of arguments")
    exit(1)
```

```python
    if len(argv) < 2:
        exit_piman()

    if argv[1] == "server":
        server()
    elif argv[1] == "restart":
        if len(argv) < 3:
            exit_piman()
        restart(argv[2], argv[3:])
    elif argv[1] == "reinstall":
        if len(argv) < 3:
            exit_piman()
        reinstall(argv[2], argv[3])
    elif argv[1] == "config":
        config_ui(argv[2], argv[3], argv[4])

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
   
## **power_cycle.py**     
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
The turn_off function will turn off the pi at the specified port.  

def turn_off(port):
```python
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
The turn_on function will turn on the pi at the specified port  
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

## **About the OID...**
---   
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

    `python3 piman.py reinstall 172.30.4.254 2` -> reinstalls pi 2 for the switch 172.30.4.254
    
* Config - To launch the configuration webserver, you can run the following command:

    `python3 piman.py config <organization name> <path to config.yaml> <path to hosts.csv>`

    Example: 

    `python3 piman.py config Dubai ./.yaml ./hosts.csv` -> launches configuration server for .yaml and hosts.csv in the root folder.



## **DHCP**
---
The DHCP server utilized for this project is a very lightweight, barebone version of [this DHCP server](https://github.com/niccokunzmann/python_dhcp_server). To manually assign IPs to known MAC addresses, you can modify the `hosts.csv` file located in the root of the main directory. The Pis will send a DHCP packet to the manager which in then responds with an IP and the location of the TFTP server. 
Navigate to `dhcp/README.md` to read more about DHCP.    

## **TFTP**    
---    
The TFTP server is responsible for serving the boot files needed for each node to start-up correctly. The TFTP code is pretty straightforward, but here's somethings to look out for: 

* The TFTP server serves files from `install/boot` directory
* **You must put `rootfs.tgz` inside this directory** 
* You can edit `hello_protocol.sh` located in `install/initram` directory. **Be sure to run `install/initram/create_initramfs.gz` to create the `initramfs.gz `**. Please note that `create_initramfs.gz` has been updated to place the created zip in the `install/boot` directory. 
Navigate to `tftp/README.md` to read more about TFTP.    

## **TCP**   
---   
The server side of Hello Protocol is implemented here.    
The `/etc/rc.local` file has been updated on the manager and the nodes to run the server and monitoring tools from startup. Take a look at it for each machine to get a better understanding of the startup process.    
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

### **Configuration and Alerts**    
To customize the timeout between each system check and/or the thresholds to alert, you can edit the `monitoring/monitoring.config`. 


Currently the system send a slack message to `#ice2` channel. You can create a slack app and set up webhooks to link your channel to the system. Follow [this](https://get.slack.help/hc/en-us/articles/115005265063-Incoming-WebHooks-for-Slack) slack tutorial.

## Grafana Dashboard    
--- 
Grafana Dashboard visualizes the data gathered by monitoring.

Attention: Grafana is dependent on monitoring, so make sure monitoring is setup and working before working on this

### Installation

To install Grafana, Follow the instructions [here](https://grafana.com/grafana/download?platform=linux) for your OS

Then install the SimpleJson Plugin from [here](https://grafana.com/grafana/plugins/grafana-simple-json-datasource) so Grafana can read JSON data

### Run

#### Mac

Run
```bash
brew tap homebrew/services
```
then
```bash
brew services start grafana
```

Finally, go to [http://localhost:3000](http://localhost:3000) to open Grafana. Login using username: admin and password: admin

#### Windows

Follow [these](https://grafana.com/docs/installation/windows/) instructions

#### Debian/Ubuntu

Follow [these](https://grafana.com/docs/installation/debian/) instructions

#### NOTE: After logging in, "Install Grafana" should be crossed out if you installed everything properly. Go to [here](https://grafana.com/docs/installation/requirements/) for more Information

### Grafana Set Up on VM

Make sure to put ```grafana.py ``` file or code next to the "logs" folder from monitoring. If you place the file somewhere else, make sure to change the paths accordingly.

Next, place the ```grafana.sh ``` or code next to the ```grafana.py ``` file with the monitoring code. This executable will install ```bottle``` package and run grafana server

Run following to make the file a executable
```bash
chmod +x grafana.sh
```

Finally, add the ```grafana.service``` file or code next to the ```monitoring.service``` file you created for monitoring and run the service. If all paths are correct, the service should run.

#### Note: Make sure to update paths in case you are running these files from your own directories

#### Now your VM is ready to send the monitoring data to Grafana

### Running Dashboard

After, completing the previous step, run 
```bash
ssh -R 80:localhost:8081 ssh.localhost.run
```

This command makes the ```localhost``` of the VM accessible from outside. After the command, two URLs will be generated. Pick one, you will need it for the following steps.

Now, go back on Grafana on your Web Browser and click "Add Data Source". Search for SimpleJson and choose it.

Name the Data Source whatever you like, place the URL you picked in the URL field and click "Save & Test". A message should popup telling you if connection was successful.

#### Now Your VM is connected to Grafana on [http://localhost:3000](http://localhost:3000)

Finally, click the four square button under the "+" button and click 'New Dashboard'. After the Dashboard is created, click "Add Query" then click the 'Query' dropdown and pick your Data Source.

Now, click the "Select Metric" next to 'timeserie" and choose the monitoring data you want visualize. 

From here, you can see data from last 6 hours but you can change the range if you want to check status from last night for example.

You can also set the dashboard to update every 5 sec or the duration of your choosing.

#### Shutting Grafana Down

When done, click "CTRL-C" on the VM to stop the connection from your VM to Grafana.

Then run (on Mac)
```bash
brew services stop grafana
```

to stop Grafana on your computer. Or follow the respective steps to stop Grafana on Windows and Linux.


### Start Up Scripts   
The `/etc/rc.local` file has been updated on the manager and the nodes to run the server and monitoring tools from startup. Take a look at it for each machine to get a better understanding of the startup process. 

## **Logs**
All print statements will be redirecting to `logs` folder with format YEAR-MONTH-DATE_hour:minutes.log in logs folder.

## **NTP Server** 
Used a NTP server found here: https://github.com/limifly/ntpserver, minor bugs fixed
The process for setting up the ntp client on pi's is explained here: http://raspberrypi.tomasgreno.cz/ntp-client-and-server.html
The tally codes in 'ntpq -pn' are listed in: https://linux.die.net/man/8/ntpq

To get ntp setup you must 'sudo apt-get install ntp' on the pi. 

Then you want to stop the timesyncd service:

```
systemctl stop systemd-timesyncd
systemctl disable systemd-timesyncd
​/etc/init.d/ntp stop
​/etc/init.d/ntp start
```
After go into '/etc/ntp.conf' and remove the servers:

```
# pool.ntp.org maps to more than 300 low-stratum NTP servers.
# Your server will pick a different set every time it starts up.
# *** Please consider joining the pool! ***
# *** ***
server 0.cz.pool.ntp.org iburst
server 1.cz.pool.ntp.org iburst
server 2.cz.pool.ntp.org iburst
server 3.cz.pool.ntp.org iburs
```

Then restart the pi and DHCP will populate the '/run/ntp.conf.dhcp' file with the vm as a NTP server, the ip is taken from the vm ip in piman.conf

You can check the list of servers with 'ntpq -pn' and after the ntp server receives and sends a few messages there should be a '*' meaning that it is the selected ntp server the client is getting the time from.

The NTP server has its own thread in piman.py, on start it creates a socket that listens for ntp messages from all reachable ip's on port 123. The file has two threads a worker and reciever. The receiver will see requests on the 
soccket and open up another socket to receive data from the client, it times this and enqueques the final time and address of the client. The worker will dequeue and send  the needed times to the requesting client. 

If testing you can type 'sudo /etc/init.d/ntp restart' on the pi to have the client to instantly send a ntp message to the server.


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
    
* To test if a pi successfully booted up, ping the ip address it was assigned. Alternatively, ssh into that ip_address. *

