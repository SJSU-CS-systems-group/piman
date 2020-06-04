## Piman Installation Guide

### Introduction

This is a guide to set up and install Piman ([Bitbucket Repo](https://bitbucket.org/br33d/piman/src/master/)) to a Raspberry Pi. Piman is a network management software. 

### System Requirements

* A linux-based terminal is required to clone and edit the code base locally. If running Windows OS, we recommend using Ubuntu for Windows which can be found [here](https://tutorials.ubuntu.com/tutorial/tutorial-ubuntu-on-windows#0).

* SJSU Network connection 
	* If not on SJSU network, view *Installation* details for VPN 

### Installation

#### Cisco Any Connect
If not connected to SJSU wifi, a VPN is required to access the Piman VM. SJSU uses [Cisco Any Connect](https://www.sjsu.edu/it/services/network/vpn/index.php).

Example: 

![VPN picture](https://lh3.googleusercontent.com/KMVN_c0TfFR8NcOqR-UKd-Dqvsj3sjjds_9Y9o7UvLBPiwziTf9ZCQI6_Ue3VF2qHfnUVLkImqCEb4MVznrHaCn_mLOgOnFCMMvBC3_SmqADYs0NGOGPYLDadev5ygJSOoFv2Opa)

![VPN login](https://lh6.googleusercontent.com/MWG40sH8KB6jDYZXZVlrLbkwA9WflJD8anQw5X6vItJZ5VLHrTCjPFbwq-b1jbFxw9g4H5xx51nshn1SH9o79mU5c9ir9By8RJOYuto)

### Set up

1. #### Connect to the VM
	* Using your terminal, ssh into your VM using your SJSU school ID and password.
	`ssh <your-school-ID>@cs-reed-<your-switch-#>.cs.sjsu.edu`
	
	Example: 

	![VM connect](https://lh4.googleusercontent.com/FSM_B8zijUlAbpHNVH5a2KSGuJO5-1vv4wYaMcGVM9NIeNiHv8PctwxmR3ehzVCqnTWzDn-mUI3KTCOJERkLfjw30WcyyRDGKVQM-MvI)
	

2. #### Connect to the network with the raspberry pis.
	* ssh into your assigned group/city name using the default user (cs158b) and provided password.
	`ssh cs158b.<groupname>`
	* Create your own account and password (do not reuse passwords)
	`sudo adduser --ingroup sudo <your new username>`
	
	Example:

	![root login](https://lh3.googleusercontent.com/rqido5VIak7U05RKNUr6RasSVj_ffNzvoLTspMQVUjLxyDbAPJY37rzKDl0DpW7nl4ZQewnDUsI9ktTWFM8AZH6Zf4vwJ4sdDSDN8AY)
	![add user](https://lh4.googleusercontent.com/7LbJ4oEyMLyabyaVU_IOs5lpyB0J41ApVspDU3B1FZ_cIGKPrJVsZzm9hvPU1qlf__OQESUAHP9xcAI2myAtTjw1n0t_ErucuZVN8xcC4uIw16ZWKPtmkjmacLDVqSprGGwEeoBl)
	![login](https://lh6.googleusercontent.com/Lr6S08KUJXTWHwR_ATsAYNgbzEcvy4ltjgRUDXhPlDcwsne4mIsEZXci7nGWgejlRf1YHwUVVe5-zFbeC13nxRpXhf6LXasQ_tj24nkm0QFaKDabIRos5cSsHpOyDB7cwvL05BtS)



3. #### Clone the repo on the network VM
	`git clone https://<bitbucketusername>@bitbucket.org/br33d/piman.git`

	Example:

	![cloning](https://lh5.googleusercontent.com/W9UcI0AX0uqKJHLmmtBLWUGZsspKnyDZsVDTM0vgRL8tyB5NjtpEXxYFgS0GZ8rYLfXRcTQ9E8kmBJKKv_8fO1Pq8o8m4u6Dz98HvL0WFMBLouaFbqXjXicaj13DhPubDqJf-Hr_)


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

	‘Python3 piman.py config <organization name> <path to config.yaml> <path to hosts.csv>’

	![config setup](https://lh6.googleusercontent.com/XYlNxH9ZD4OFMiq-xLjClBEFWKwaBFEyz6CcYTuLFkgxVNg6CT7UUx2CEFKSjUtKTwa0UxjmDnuwkQA1U9drckqtkgkTWSiO2rEoE2fE)

	If PiMan is hosted on a VM and you'd like to access the configuration UI from a different client, you can use 'ssh -N -L 5000:localhost:5000 name@city'.  Replace name@city to be the VM login that you would like to link to.  You should now be able to connect to the webserver by going to 'localhost:5000' in your browser.

	![connect 5000](https://lh6.googleusercontent.com/tO6aIphSFyNeW_X7Q-MW3GHB_UoQgQnuHeZ9H9fOlbwzwI2Zlc9fBTCvuyvEItrYMrC-3Akb2DuDa0svwiu0XCMuclhZfDWZ37PqIQkMM9ypfdm40rQO-aiGsyiNO7zX8XRFOqJA)

	![UI](https://lh5.googleusercontent.com/rch1Vupq6UurVhi-OLDL2hLisF0BEIRzSuzjp6ggC13lRJ2RUdm3SFT9EqZI9HneBr6I3XNSc4XxYJT74vVQAtttqTEvv5RKOoyFSlaA5LrK8MKILfiBW6R5qZoCzUepZjy6izU7)

	Navigate to the webserver, hosted on port 5000.  If you are accessing the webserver from the same machine, you can use localhost:5000 in any browser.  Click on 'CONFIG' to generate the configuration file and begin configuration.  Click on 'HOSTS.CSV' to generate the hosts file and begin configuration for that.  Remember to click the apply changes button before navigating to a different page.  Once you are done applying changes, restart piman manually for those changes to take effect.

	By default, the webserver will modify the files .yaml and hosts.csv in the root directory of PiMan.

	![Config settings](https://lh4.googleusercontent.com/m9bDdR_XOgYbgbm3z6jG3nGDRN9qSEyZPVs3xq3ZeI6gt8xGkvLktC4Fmx9x-I1JGs2w8SAINbzGDgaYgbIkfASM8_nQ2xbXfk1bXpEfj5h0WMlAonAmSe94pJYmQMiU0L7_oYcG)

	Get the MAC addresses by running the mac mapper. The pis MACs start with ‘B8’.

	![Mac Mapper](https://lh5.googleusercontent.com/tGFLfa3fazaj2k_PIYRbvmACXH8Qfo9itTj1OA_Z73GF0ZQhlB5vaQIuIyZ0T4EEQsT_i6uQP5CsxCgkM4V0KObcYv9hIajDGsUbeTtDk_6cFshKm6NGCfm0mhgoo-Tol5ihU1ed)

	Put the mac addresses in the hosts.csv config along with an IP that you assign, your group name and any time (the time will be changed the next time you run the server)

	![Hosts settings](https://lh5.googleusercontent.com/oKtV_PtlRjw0W3Jvkw-5yxI7lWF5ozMTXuCWW3VMbPwnOsH3oFDFaZQjVaqDth99rv43WXysfUTP3gV8XYGo005a_JFD9FMLeZ9YypuV)


	##### Config Format

	If you would like to configure PiMan manually instead of using the UI, follow this format.  To configure piman, create a YAML file with the following format:

	```
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
	  - switch_address: 172.30.4.254
	    pi_addresses:
	      - 172.30.4.13
	      - 172.30.4.14
	      - 172.30.4.15
	      - 172.30.4.16
	      - 172.30.4.17
	      - 172.30.4.18
	      - 172.30.4.19
	      - 172.30.4.20
	  - switch_address: 172.30.4.128
	    pi_addresses:
	      - 172.30.4.1
	      - 172.30.4.2
	      - 172.30.4.3
	      - 172.30.4.4
	      - 172.30.4.5
	      - 172.30.4.6
	```


5. #### Monitoring

	cd into "monitoring" folder
	There are 4 files and 1 folder: (only monitoring-server.py go on the Pi)
		monitoring-client.py (VM)
		monitoring-server.py (Pi)
		monitoring.config (VM)
		monitoring_piman.sh (VM)
		logs (folder) (VM)

	Step 1: Set Up systemd to run the monitoring_piman.sh on the VM
		cd into /etc/systemd/system
		create a new monitoring service with the name: monitoring.service (ex: sudo nano monitoring.service)
		Copy this content into monitoring.service
			[Unit]
			Description=Raspberry Pi Monitoring Manager
			After=network.target

			[Service]
			Type=simple
			WorkingDirectory=/usr/bin/piman/monitoring
			ExecStart=/usr/bin/piman/monitoring/monitoring_piman.sh
			Restart=always
			RestartSec=15
			User=root

			[Install]
			WantedBy=multi-user.target
		Make sure the monitoring folder is located under /usr/bin/piman or you can change the directory that match the service

	![Monitoring.service](https://lh3.googleusercontent.com/WGogoGHIl8q4Vb04dOjmbRSEUZ9CMzTH8EHknCiP15udrCti8LryFpnZYtIjXW5mSsN9AmqicDoOTUk8VvduY3wONEhLk21qWdGD5f5wVBDVnsdDzf7EsUzl13SViwmfVAmfUC8Z)

	Note: run python3 -m pip install requests to install the requests function

	Step 2: Set up Slack channel for alerting in the monitoring.config
		Go into Slack Setting
		Search for Incoming Webhook
		Add to Slack and choose the channel you want to Monitoring Service alert to. 
		Copy the WebHook URL and put it into monitoring.config on line "slack= ..."

	![webhooks](https://lh5.googleusercontent.com/1baAEkHG-v2nstRK_ZXLBGaZHI3LC7OpSYDk_qFbrHY43tFA3teObAfjMUUpw9wIv_w7QFajIy0fdfueexP-qhh-ZtA8G_7-INBxJgO7luEW-po4YdA9AMHwgBAB1xIVgufe5cK3)

	Step 3: Run the systemd service on VM
		To run systemd service.
		sudo systemctl start monitoring
		Check for status: systemctl status monitoring

	Sept 4: Distribute monitoring-server.py to each of the Pi.
		Copy monitoring-server.py and place it on the Pi

	Step 5: Change DNS server to connect the Pi to the Internet (temporarily fix)
		Open /etc/resolv.conf
		Change the ip address to 8.8.8.8 or any DNS server
		Because we already set up IP table on the VM we can test the connection by Ping any website( ping google.com)
		If fail, check step 1 make sure it run correctly

	Step 6: Set up systemd to run the monitoring-server.py on the Pi
	After the Pi connect to the Internet. Run 2 command below under ROOT (very important)
	sudo su
	python3 -m pip install flask-restful
	python3 -m pip install psutil

	Create a monitoring service (sudo nano /etc/systemd/system/monitoring.service)
		[Unit]
		Description=Raspberry Pi Manager
		After=network.target

		[Service]
		Type=simple
		WorkingDirectory=/usr/bin/piman
		ExecStart=/usr/bin/env python3 /usr/bin/piman/monitoring_server.py
		StandardOutput=syslog
		StandardError=syslog
		Restart=always
		RestartSec=15
		User=root

		[Install]
		WantedBy=multi-user.target
	Making sure the WorkingDirectory and ExecStart point match the monitoring_server.py location

	Step 7:	Run the systemd service on the Pi
		systemctl start monitoring

	Now we can see data log in log/monitor.log and if there are any error, it will notify on the Slack channel that we set up in step 2

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

	Run following to make the file an executable
	```bash
	chmod -x grafana.sh
	```

	Finally, add the ```grafana.service``` file or code next to the ```monitoring.service``` file you created for monitoring and run the service. If all paths are correct, the service should run. Make sure you path to where your monitoring folder is, it may be different than the given example.

	![grafana.service](https://lh3.googleusercontent.com/Xbww-R1aO23VF1_DCuAbgpdE-e63ilJiFSVOWeT5x6Dxy_OuuXbUel7xBLUhiVwiaav4Bkk_KWpeG-Z61xMPuqHx3j-FnVic3bl6bKGm)


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
