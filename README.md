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

Included in PiMan is a user-interface designed to allow easier setup of configuration and pis.  Use the piman config launch option shown above.  Navigate to the webserver, hosted on port 5000.  If you are accessing the webserver from the same machine, you can use localhost:5000 in any browser.  Click on 'CONFIG' to generate the configuration file and begin configuration.  Click on 'HOSTS.CSV' to generate the hosts file and begin configuration for that.  Remember to click the apply changes button before navigating to a different page.  Once you are done applying changes, restart piman manually for those changes to take effect.

By default, the webserver will modify the files .yaml and hosts.csv in the root directory of PiMan.

If PiMan is hosted on a VM and you'd like to access the configuration UI from a different client, you can use 'ssh -N -L 5000:localhost:5000 name@city'.  Replace name@city to be the VM login that you would like to link to.  You should now be able to connect to the webserver by going to 'localhost:5000' in your browser.

#### Config Format

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

### Logs
all print statements will be redirectiong to logs folder with format YEAR-MONTH-DATE_hour:minutes.log in logs folder

## NTP Server 
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
