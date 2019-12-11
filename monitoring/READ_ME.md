cd into "monitoring" folder
There are 4 files and 1 folder: (only monitoring-server.py go on the Pi)
	monitoring-client.py (VM)	(line 70, change the IP address match your pi)
	monitoring-server.py (Pi)
	monitoring.config (VM)
	monitoring_piman.sh (VM)
	logs (folder) (VM)

Step 1: Set Up systemd to run the monitoring_piman.sh on the VM
	cd into /etc/systemd/system
	create a new monitoring service with the name: monitoring.service (ex: sudo nano monitoring.service)
	Copy this content into monitoring.service
		[Unit]
		Description=Raspberry Pi Monitoirng Manager
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

Note: run python3 -m pip install requests to install the requests function

Step 2: Set up Slack channel for alerting in the monitoring.config
	Go into Slack Setting
	Search for Incomming Webhook
	Add to Slack and choose the channel you want to Monitoring Service alert to. 
	Copy the WebHook URL and put it into monitoring.config on line "slack= ..."

Step 3: Run the systemd service on VM
	To run systemd service.
	sudo systemctl start monitoring
	Check for status: systemctl status monitoring

Sept 4: Distribute monitoring-server.py to each of the Pi.
	Copy monitoring-server.py and place it on the Pi

Step 5: Change DNS server to connect the Pi to the Internet (temporaty fix)
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


