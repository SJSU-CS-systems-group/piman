![Team Ice Logo](assets/img/team-ice.png)

This repository will contain the project work done by the members of Team Ice throughout the course of the Fall 2018 semester in CS 158B.
---
## Piman 

Piman has multiple different functionalities 

* Server - To run the piman server in the background and allow logging run the following command:

    `python3 piman.py server & > logs/piman.log`

    With this command, piman runs the DHCP, TFTP, and TCP server in the background and redirects the standard out to `logs/piman.log` file. 

* Restart - To restart a set of pis, you can run the following command:

    `python3 piman.py restart [list of pi_numbers]`

    Example: 

    `python3 piman.py restart 2 3 4` -> restarts pi 2, 3, and 4. 

* Reinstall - To reinstall a set of pis, you can run the following command:

    `python3 piman.py reinstall [list of pi_numbers]`

    Example: 

    `python3 piman.py reinstall 2 3 4` -> reinstalls pi 2, 3, and 4. 

    **Note**: This functionality is not complete yet, it will require some bug fixes in the TCP and Hello Protocol. 

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