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

## Grafana Dashboard

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
chmod -x grafana.sh
```

Finally, add the ```grafana.service``` file or code next to the ```monitoring.service``` file you created for monitoring and run the service. If all paths are correct, the service should run.

#### Now your VM is ready to send the monitoring data to Grafana

### Running Dashboard

After, completing the previous step, run 
```bash
ssh -R 80:grafana:8080 ssh.localhost.run
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