## Piman Installation Guide

### Introduction

This is a guide to set up and install Piman ([GitHub Repo](https://github.com/SJSU-CS-systems-group/piman/)) to a Raspberry Pi. Piman is a network management software. 

### System Requirements

* A linux-based terminal is required to clone and edit the code base locally. If running Windows OS, we recommend using Ubuntu for Windows which can be found [here](https://tutorials.ubuntu.com/tutorial/tutorial-ubuntu-on-windows#0).

* SJSU Network connection 
	* If not on SJSU network, view *Installation* details for VPN 

### Installation

#### OpenVPN
If not connected to SJSU wifi, a VPN is required to access the Piman VM. SJSU uses [OpenVPN](https://openvpn.net/download-open-vpn/).

After downloading and installing OpenVPN Connect, you will also need a certificate file and a private key for your team to access the VPN. The Instructor will provide both of these for you.

Example: 

![VPN picture](https://i.imgur.com/Zd7VRdo.png)

### Set up

1. #### Connect to the VM
	* Using your terminal, ssh into your VM using cs158b as the username and the provided password.
	`ssh cs158b@{VM_IP}
	
	Example: 

	```
	ssh cs158b@172.31.1.254
	```
	

2. #### Creating other Accounts (optional)
	* Create your own account and password (do not reuse passwords)
	`sudo adduser --ingroup sudo <your new username>`
	
	Example:
	
	```
	sudo adduser --ingroup sudo guest
	```


3. #### Clone the repo on the network VM
	`git clone https://<bitbucketusername>@bitbucket.org/{repo_name}`

### **A Note to Our Readers...**
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


4. #### Set up your configuration

##### Configuration UI

Included in PiMan is a user-interface designed to allow easier setup of configuration and pis.  Use the piman config launch option shown above.  

‘Python3 piman.py config {project_name} {path/to/config.yaml} {path/to/hosts.csv}’

![config setup](https://i.imgur.com/CLgEUD2.png)

If PiMan is hosted on a VM and you'd like to access the configuration UI from a different client, you can use 'ssh -N -L 5000:localhost:5000 {usr}@{VM_IP}'. You should now be able to connect to the webserver by going to 'localhost:5000' in your browser.

![connect 5000](https://lh6.googleusercontent.com/tO6aIphSFyNeW_X7Q-MW3GHB_UoQgQnuHeZ9H9fOlbwzwI2Zlc9fBTCvuyvEItrYMrC-3Akb2DuDa0svwiu0XCMuclhZfDWZ37PqIQkMM9ypfdm40rQO-aiGsyiNO7zX8XRFOqJA)

![UI](https://lh5.googleusercontent.com/rch1Vupq6UurVhi-OLDL2hLisF0BEIRzSuzjp6ggC13lRJ2RUdm3SFT9EqZI9HneBr6I3XNSc4XxYJT74vVQAtttqTEvv5RKOoyFSlaA5LrK8MKILfiBW6R5qZoCzUepZjy6izU7)

Navigate to the webserver, hosted on port 5000.  If you are accessing the webserver from the same machine, you can use localhost:5000 in any browser.  Click on 'CONFIG' to generate the configuration file and begin configuration.  

Config Options:

* Private Number: This is your VLAN number
* Interface: The name of the interface that the switches are on
* Server_Address: The IP Address that the VM uses for the Piman server
* Subnet Mask: The Subnet Mask for the Server Address
* Switch_Count: The number of switches in use
* Switch_Address: The IP Address of a Switch
* PI_Address: The IP Address of the Pi connected to the Switch

Click on 'HOSTS.CSV' to generate the hosts file and begin configuration for that.  Remember to click the apply changes button before navigating to a different page.  Once you are done applying changes, restart piman manually for those changes to take effect.

By default, the webserver will modify the files .yaml and hosts.csv in the root directory of PiMan.

![Config settings](https://lh4.googleusercontent.com/m9bDdR_XOgYbgbm3z6jG3nGDRN9qSEyZPVs3xq3ZeI6gt8xGkvLktC4Fmx9x-I1JGs2w8SAINbzGDgaYgbIkfASM8_nQ2xbXfk1bXpEfj5h0WMlAonAmSe94pJYmQMiU0L7_oYcG)

Get the MAC addresses by running the mac mapper. 

To run the Mac Mapper, use the command sudo python3 ./build/piman.pyz mapper {VM_IP_Address} {Interface_Number} {PI_Number}

Example:
	
	sudo python3 ./build/piman.pyz mapper 172.31.1.254 1 1

Note: The pi-3s' MAC Addresses start with ‘B8’ and the pi-4s' MAC Addresses start with 'DC'.

![Mac Mapper](https://media.discordapp.net/attachments/763085755043282988/771921564496297994/2020-10-30_19_20_09-cs158bmanchester___manchester.png?width=616&height=429)

Put the mac addresses in the hosts.csv config along with an IP that you assign, your group name and any time (the time will be changed the next time you run the server)

![Hosts settings](https://i.imgur.com/9MmXbcZ.png)


##### Config Format

If you would like to configure PiMan manually instead of using the UI, follow this format.  To configure piman, create a YAML file with the following format:

	
	private_number:
	server_address:
	subnet_mask:
	interface: 
	switch_count:
	switches:
	  - switch_address:
	    pi_addresses:
	      -
	      -
	      -
	  - switch_address:
	    pi_addresses:
	      -
	      -...
	

For example:
	
	private_number: 4
	server_address: 172.31.4.1
	subnet_mask: 255.255.255.0
	interface: ens4
	switch_count: 2
	switches:
	  - switch_address: 172.31.4.254
	    pi_addresses:
	      - 172.30.4.13
	      - 172.30.4.14
	      - 172.30.4.15
	      - 172.30.4.16
	      - 172.30.4.17
	      - 172.30.4.18
	      - 172.30.4.19
	      - 172.30.4.20
	  - switch_address: 172.31.4.128
	    pi_addresses:
	      - 172.30.4.1
	      - 172.30.4.2
	      - 172.30.4.3
	      - 172.30.4.4
	      - 172.30.4.5
	      - 172.30.4.6
	


5. #### Monitoring

	cd into "monitoring" folder
	There are 4 files and 1 folder: (only monitoring-server.py go on the Pi)
		monitoring-client.py (VM)
		monitoring-server.py (Pi)
		monitoring.config (VM)
		monitoring_piman.sh (VM)
		logs (folder) (VM)

	**Step 1: Set Up systemd to run the monitoring_piman.sh on the VM**
		create a new monitoring service with the name: monitoring.service (ex: sudo nano monitoring.service) in the monitoring folder
		Copy this content into monitoring.service
		
			[Unit]
			Description=Raspberry Pi Monitoring Manager
			After=network.target

			[Service]
			Type=simple
			WorkingDirectory=/home/usr/local/piman/monitoring
			ExecStart=/home/usr/local/piman/monitoring/monitoring_piman.sh
			Restart=always
			RestartSec=15
			User=root

			[Install]
			WantedBy=multi-user.target
			
	* Make sure the monitoring folder is located under /home/usr/local/piman or you can change the directory to match the service

	Now, link the service file into the systemd using ln -s /home/usr/local/piman/monitoring/monitoring.service /etc/systemd/system

	**Step 2: Set up Slack channel or Discord channel for alerting in the monitoring.config**
	
	## Slack
	
	* Go into Slack Setting		
	* Search for Incoming Webhook
	* Add to Slack and choose the channel you want to Monitoring Service alert to.
	* Copy the WebHook URL and put it into monitoring.config on line "slack= ..."
	* In monitoring-client.py alert() function
		* Ensure the bolded portion is **slack** "url = monitor_config['DEFAULT']['**slack**']"
		* Ensure the bolded portion is **text** "data=json.dumps({'**text**': '{}'.format(data), 'username': 'Piman'})"
	
	## Discord
	
	* On the server settings, go to integration, then go to webhooks
	* Then, click the New Webhook button, then copy the URL
	* Place the URL into the monitoring.config file on line "discord=..."
	* In monitoring-client.py alert() function
		* Ensure the bolded portion is **discord** "url = monitor_config['DEFAULT']['**discord**']"
		* Ensure the bolded portion is **content** "data=json.dumps({'**content**': '{}'.format(data), 'username': 'Piman'})"
	
	Here's what the monitoring.config file should look like:
	
		[DEFAULT]
		slack = {slack_webhook_url}
		discord = {discord_webhook_url}
		timeout = 300
		pids_threshold = 100
		mem_threshold = 70.0
		disk_threshold = 50.0
		cpu_threshold = 50.0
		temperature_threshold = 85.0
				
	**Step 3: Run the systemd service on VM**
	
	To run systemd service:
		
	* sudo systemctl start monitoring
	* Check for status: systemctl status monitoring
	* To have monitoring service run on boot up: sudo systemctl enable monitoring

	**Step 4: Distribute monitoring-server.py to each of the Pi.**
	
	To Place monitoring-server.py on a pi, while in the monitoring folder, use the command scp monitoring-server.py pi@{pi_address}:~ where {pi_address} is the IP address of the pi you are placing the file into
	
	* EX: if our pi's IP address is 172.16.1.1, we would do scp monitoring-server.py pi@172.16.1.1:~ to copy the file to the pi

	**Step 5 Set up systemd to run the monitoring-server.py on the Pi**
	
	First, ssh into the pi using ssh pi@{pi_address}. Then, make sure the dependencies are installed using the following commands:
	
	* sudo apt-get update
	* sudo apt-get install python3-pip
	* sudo apt-get install python3-dev
	* sudo python3 -m pip install flask-restful
	* sudo python3 -m pip install psutil

	Create a monitoring service (sudo nano monitoring.service)
	
		[Unit]
		Description=Raspberry Pi Manager
		After=network.target

		[Service]
		Type=simple
		WorkingDirectory=/home/pi/piman
		ExecStart=/usr/bin/python3 /home/pi/monitoring_server.py
		StandardOutput=syslog
		StandardError=syslog
		Restart=always
		RestartSec=15
		User=root

		[Install]
		WantedBy=multi-user.target
		
	* Making sure the WorkingDirectory and ExecStart point match the monitoring_server.py location
	
	Then, create a link to the service file into systemd using ln -s /home/pi/monitoring.service /etc/systemd/system

	**Step 6:	Run the systemd service on the Pi**
	
	Run the command sudo systemctl start monitoring. Then, use sudo systemctl status monitoring to make sure it is running

	If everything is set up correctly, we can now see data log in log/monitor.log on the VM and if there are any errors or if the pi's go over the thresholds set it monitoring.config, it will notify on the Slack or Discord channel that we set up in step 2

	## To add a new metric to monitor
	
	* monitoring.config
		* Add the metric threshold underneath "temperature_threshold = 85.0"
	* grafana.py
		* In the parse() function
			* Before "cpu_load = float(pi[-5].replace("CPU load: ", "").replace(" ", ""))", add the new metric you would like monitor following the same format (the next metric would be at index -6)
			* Before the if/else block for CPU in the try block, add the new metric following the same format
			* Before the if/else block for CPU in the except block, add the new metric following the same format
	* monitoring-client.py
		* In the pretty_stats() function
			* Add a new description in the formatted string for event['**new metric**']
		* In the check_response() function
			* Add a new if block for your new metric following the same format. Note: use the same name for monitor_config[**new metric**] as the name that is specified in monitoring.config and use the same name for response_dict[**new metric**] as what is specified in monitoring-server.py
	* monitoring-server.py
		* In the get() function in Pimon class
			* Use the following documentation https://psutil.readthedocs.io/en/latest/ to add a new metric with psutil under the "temperature = psutil.sensors_temperatures().get('cpu_thermal')[0][1]" line. Note: Make sure the return value is a number and not an array/object
			* Add the metric to the "event" mapping underneath "temp"

6. #### Grafana Dashboard

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
	
	Finally, link the ```grafana.service ``` file using ```ln -s /home/usr/local/piman/monitoring/grafana.service /etc/systemd/system ```, then do ```sudo systemctl start grafana ```, and ```sudo systemctl enable grafana ```


	#### Note: Make sure to update paths in case you are running these files from your own directories

	#### Now your VM is ready to send the monitoring data to Grafana

	### Running Dashboard

	Now, go back on Grafana on your Web Browser and click "Add Data Source". Search for SimpleJson and choose it.

	Name the Data Source whatever you like, place the URL of the virtual machine at port 8081 (ex: 172.31.1.254:8081) in the URL field and click "Save & Test". A message should popup telling you if connection was successful.

	#### Now Your VM is connected to Grafana on [http://localhost:3000](http://localhost:3000)

	Finally, click the four square button under the "+" button and click 'New Dashboard'. After the Dashboard is created, click "Add Query" then click the 'Query' dropdown and pick your Data Source.

	Now, click the "Select Metric" next to 'timeseries" and choose the monitoring data you want visualize. 

	From here, you can see data from last 6 hours but you can change the range if you want to check status from last night for example.

	You can also set the dashboard to update every 5 sec or the duration of your choosing.

### Running Piman

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

    `python3 piman.py config Dubai ./piman.yaml ./hosts.csv` -> launches configuration server for piman.yaml and hosts.csv in the root folder.


### Troubleshooting

1. Port taken error 
	*  When the service is already started and there is an attempt to access the port/network in setting up the Pi, there may be an error similar to this:
	![port taken](https://lh4.googleusercontent.com/PjnLDHdwJWLX4HZNd8FHhwew05yWP-fFGnoz7WBOYtEukIXItxpFrpSJizl8hX6thhe3kJycxUu6SvTisuv0Sao2fwUg-GqaRnKu9zyJ7c9fKGYLfY9v78PAVVSuEYslXCE9cENH)

	* Fix 1: Check if piman service is running on systemd
	* Fix 2: open all running processes and kill the ones that should not be running

2. Further errors/fixes compiled by CS158B Fall 19 ([Google Folder](https://drive.google.com/drive/folders/1oMbgBsLcO0yLbn9uwH1YBDJ5SVOogBhR?usp=sharing) may require SJSU email login)
	* [Bad SD Card](https://drive.google.com/open?id=1RDT4NBndLJd6D3evJHSMVisAEv6HT_2uh6J8WoTWOSQ)
	* [Set up NAT](https://drive.google.com/open?id=1cB-_gJW8hLQQkZFMa-41szuNjpYFwclN_MYGZLpxA8U)
	* [TCP Port Reading Incorrectly](https://drive.google.com/open?id=1VPx6TIb5JIcQrSwtRAe2jIevs45H8OuIFiiiF5IDouE)
	* [No SNMP Response](https://drive.google.com/open?id=1g5K58r3k9fQ-dUhCFz20WGSy2iqSqExGVCAtuAxhNk0)
	* For more troubleshooting guides, go to the **Google Folder** listed above. 
