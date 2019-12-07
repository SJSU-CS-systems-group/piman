# Piman

## Raspberry Pi network management software  

Piman has multiple different functionalities 

* Server - To run the piman server in the background and allow logging run the following command:

    `python3 piman.py server & > logs/piman.log`

    With this command, piman runs the DHCP, TFTP, and TCP server in the background and redirects the standard out to `logs/piman.log` file. 

* Restart - To restart a set of pis, you can run the following command:

    `python3 piman.py restart <switch number> [list of pi_numbers]`

    Example: 

    `python3 piman.py restart 172.30.4.254 2 3 4` -> restarts pi 2, 3, and 4 for the switch 172.30.4.254 

* Reinstall - To reinstall a set of pis, you can run the following command:

    `python3 piman.py reinstall <switch number> [pi_number]`

    Example: 

    `python3 piman.py reinstall 172.30.4.254 2` -> reinstalls pi 2 for the switch 172.30.4.254
    
* Config - To launch the configuration webserver, you can run the following command:

    `python3 piman.py config <organization name> <path to config.yaml> <path to hosts.csv>`

    Example: 

    `python3 piman.py config Dubai ./.yaml ./hosts.csv` -> launches configuration server for .yaml and hosts.csv in the root folder.

### Set up your configuration

#### Configuration UI

Included in PiMan is a user-interface designed to allow easier setup of configuration and pis.  Use the piman config launch option shown above.  Navigate to the webserver, hosted on port 5000.  If you are accessing the webserver from the same machine, you can use localhost:5000 in any browser.  Click on 'CONFIG' to generate the configuration file and begin configuration.  Click on 'HOSTS.CSV' to generate the hosts file and begin configuration for that.

#### Config Format

If you would like to configure PiMan manually instead of using the UI, follow this format.  To configure piman, create a YAML file with the following format:

```
private_number:
server_address:
subnet_mask:
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
### DHCP Server

The DHCP server utilized for this project is a very lightweight, barebone version of [this DHCP server](https://github.com/niccokunzmann/python_dhcp_server). To manually assign IPs to known MAC addresses, you can modify the `hosts.csv` file located in the root of the main directory. The Pis will send a DHCP packet to the manager which in then responds with an IP and the location of the TFTP server. 

### TFTP Server

The TFTP server is responsible for serving the boot files needed for each node to start-up correctly. The TFTP code is pretty straightforward, but here's somethings to look out for: 

* The TFTP server serves files from `install/boot` directory
* **You must put `rootfs.tgz` inside this directory** 
* You can edit `hello_protocol.sh` located in `install/initram` directory. **Be sure to run `install/initram/create_initramfs.gz` to create the `initramfs.gz `**. Please note that `create_initramfs.gz` has been updated to place the created zip in the `install/boot` directory. 

### TCP Server

The server side of Hello Protocol is implemented here.

### Monitoring

#### Manager

There is a monitoring client running on the manager pi the periodically sends a get request to each node. The monitoring server running on the nodes respond with current status. To install the dependencies and run the client, run the following commands from the root directoyry of `pi-manager-ice`:

```sh
python3 -m pip install requests

# run server and redirect standard out to a log file
python3 monitoring/monitoring-client.py <path_to_config> > logs/status.log
```

#### Nodes
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

#### Configuration and Alerts

To customize the timeout between each system check and/or the thresholds to alert, you can edit the `monitoring/monitoring.config`. 


Currently the system send a slack message to `#ice2` channel. You can create a slack app and set up webhooks to link your channel to the system. Follow [this](https://get.slack.help/hc/en-us/articles/115005265063-Incoming-WebHooks-for-Slack) slack tutorial.


### Start Up Scripts 

The `/etc/rc.local` file has been updated on the manager and the nodes to run the server and monitoring tools from startup. Take a look at it for each machine to get a better understanding of the startup process. 