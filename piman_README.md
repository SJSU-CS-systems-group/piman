# What is piman.py?

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

#### Running the server using systemd
In order to continually run the piman server in the background even when the VM is restarted, we will use systemd and service files. First make sure the files piman.service and piman.sh are both under the same directory in /usr/local/piman. Check to see that piman.sh contains the following:
```bash
#!/bin/bash
python3 -u build/piman.pyz server
```
You should also check the piman.service file to make sure the working directory is /usr/local/piman and that ExecStart is pointing to the correct location of piman.sh It should look like the code below:
```bash
[Unit]
Description=Pi Manager

[Service]
WorkingDirectory=/usr/local/piman
ExecStart=/usr/local/piman/piman.sh
Restart=always

[Install]
WantedBy=default.target
```
Create a symbolic link from the service file to /etc/systemd/system using the command 
```bash
ln -s /usr/local/piman/piman.service /etc/systemd/system
``` 
You can check to see if the symbolic link is there by running 
```bash
ls -l /etc/systemd/system 
``` 
and seeing if piman.service -> /usr/local/piman/piman.service is there.

Finally, start the piman service, enable it so that it runs on boot and check the status to ensure it is running.
```bash
sudo systemctl start piman
sudo systemctl enable piman
sudo systemctl status piman
```

# Why piman.py?

`piman.py` exists to be the process that enables network booting and communication with raspberry pi's over the virtual network.  
This is neccessary because the pi's are being hosted on a virtual network on Ben's virtual machine.  
To do this `piman.py` is designed to use DHCP, TCP, and TFTP protocols to give the pi's ip addresses, connect to them, and transfer boot files to them.  
These protocols need to be active in order to communicate with the pi's remotely, which is why `piman.py` is implemented as a server.  

# How does it work?

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

#### Getting mac address of rasberry pi(s)
``` python
def mapper(switch_address,interface, port, file):
    for portNum in port:
        power_cycle.power_cycle(switch_address,interface, portNum)
    time.sleep(30)
    mac_mapper.mac_mapper(file)
```
`mapper()` is a function inside the `piman.py` file. It ultimately encompasses two functions `power_cycle.power_cycle()` and `mac_mapper.mac_mapper()` which will power cycle the pis causing them to try PXE boot and afterwards getting the mac address of each specified pi. This output is then printed to console as well as `mac_mapper.txt`

**How to use mapper()**

The official implementation is specified as `mapper(switch_address,interface, port)`.

`switch_address` (String) is your specified switch ip 

`interface` (int) interface remote pi’s are under, typically interface “1”

`port` (int[]) is the specified remote pi’s that you want to access

`file` (string) is an optional command that allows the user to input the discovered MAC addresses to a designated file.

**Reasons to use mapper()**



*   To get mac address of pi on specific port(s)
*   Alternate way to restart remote pi’s other than the Restart method (piman.py)

**Example**

`sudo python3 build/piman.pyz mapper {ip}.129 {interface} {port_number(s)}`

`sudo python3 build/piman.pyz mapper {ip}.129 {interface} {port_number(s)} --file {filename}`

`sudo python3 build/piman.pyz mapper 172.16.7.129 1 10 --file hosts.csv`

`sudo python3 build/piman.pyz mapper 172.16.7.129 1 1 2 3 4 5 6 7 8 9 10`

**Get Mac address of given port**

#### Starting monitoring on rasberry pis
``` python
def monitoring():
    monitoring_client.start_from_piman()
```
`monitoring()` is a function inside the `piman.py` file. This function will start the monitoring client through piman.

**Example**

`sudo python3 build/piman.pyz monitoring`

**Additional notes on monitoring**

`monitor-client.py` has been renamed to `monitor_client.py` in order to accomodate python's importing standards.


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
