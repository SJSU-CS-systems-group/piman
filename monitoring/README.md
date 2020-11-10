# Table of Contents

[Setting Up Monitoring With Grafana](#Setting-Up-Monitoring-With-Grafana)  
[Overview](##Overview)  
[Preparation](##Preparation)  
[On The VM](###On-The-VM)  
[On the Pis](###On-the-Pis)  
[Setting up the monitoring service on every Pi](##Setting-up-the-monitoring-service-on-every-Pi)  
[Setting MONITORING_LOG_PATH environment variable for monitoring service](##Setting-MONITORING-LOG_PATH-environment-variable-for-monitoring-service)  
[Setting up the monitoring client service on the VM](##Setting-up-the-monitoring-client-service-on-the-VM)  
[Setting up the grafana.py service](##Setting-up-the-grafana.py-service)  
[Installing and starting Grafana](##Installing-and-starting-Grafana)  
[Adding the SimpleJSON data source](##Adding-the-SimpleJSON-data-source)  
[Making the dashboard](##Making-the-dashboard)  

# Setting Up Monitoring With Grafana

## Overview

The monitoring service on every pi is a server which, when queried, will retrieve system data from the pi. The data currently collected includes:
* CPU load
* memory usage
* disk usage
* number of processes running
* temperature

Once retrieved, the server will respond to the query with a json object in the following format:
```
{
    "time": "Sun Nov  1 08:49:14 2020"
    "cpu_percent": 0.0,
    "memory_percent": 15.6,
    "disk_percent": 5.4,
    "num_pids": 81,
    "temp": 61.224,
}
```

Once each pi is set up with its own monitoring server, the monitoring client service must be set up on the VM. This client will poll all pi monitoring servers every 5 minutes by default. It will then store the data into the file monitor.log for human-readable logs, and this log file will be used for parsing and creating the data to serve to Grafana.

In addition, the monitoring client service will send slack or discord alerts via webhook to the url specified in monitoring.config. Alerts will only be sent out in two cases: if an exception occurred (e.g. a pi is unreachable), or if the threshold value for any of the data categories has been exceeded.

After the monitoring client service is set up, the data source service, grafana.py, must be started. This file reads in the monitor.log file from the logs directory, and creates a dictionary based on the data extracted from this file. The format of this data will correspond to Grafana's required format for timeserie data sets when the data source is SimpleJSON. For more information on this format, please consult [the SimpleJSON plugin documentation](https://github.com/grafana/simple-json-datasource). Then, a bottle web server is started on port 8081, which will be supplied to the Grafana dashboard as the link from which to collect data.

The last component to monitoring is installing Grafana itself. Grafana must be installed on the VM. Once its service is started, it will run a web server on port 3000. Through this server is how the dashboard and data panels will be set up.

The following sections will explain the steps to set up monitoring in detail.

## Preparation

The first step is to update all the pis' package repositories, install all dependencies, make all necessary directories, and copy files to the right locations.

### On the VM

1. Clone the piman directory into /usr/local:

```
cd /usr/local
sudo git clone https://github.com/SJSU-CS-systems-group/piman.git
```
This will make sure that /usr/local/piman/monitoring is a path which exists on your system.

2. Copy the monitoring.service and grafana.service files to /etc/systemd/system:

```
sudo cp monitoring.service grafana.service /etc/systemd/system
```

3. Install python dependencies:

```
sudo pip3 install requests
```


### On the Pis
1. Run the following script to initialize the pis, copy all needed files to them, and install and run the monitoring service on them:
```
cd /usr/local/piman/monitoring
sudo ./init_pis.sh pi piman /usr/local/piman/hosts.csv /usr/local/piman/monitoring
```

2. Repeat this process for all other pis.

## Setting up the monitoring service on every Pi

1. Still logged into the pi, reload the systemd daemon, start the monitoring service, and check status to make sure it is working properly:

```
sudo systemctl daemon-reload
sudo systemctl start monitoring
sudo systemctl status monitoring
```

## Setting MONITORING_LOG_PATH environment variable for monitoring service

Note: You can use another terminal editor, but the commands may be different than these

- vim ~/.bashrc

- press 'i' key
- at the top, or wherever you prefer add 'export MONITORING_LOG_PATH="relative/path/to/monitor/logfile"
- press 'esc' key
- enter ':wq' - this will save changes and exit
- enter in terminal 'source ~/.bashrc'

Note: this will permanently save your monitor file path as an environment variable and will be used in
    grafana.sh and monitoring-piman.sh

    In both, it checks if the environment variable is set and if not will exit with exit code of 1.
        If this happens, set the environment var.

    The purpose of the environment variable is to set it once and not have to worry about it again.

    you can check the output of the environment var you set with:
        - in .sh: "echo ${MONITORING_LOG_PATH}"
        - in terminal: echo $MONITORING_LOG_PATH
        both should be the same result

    If you don't 'source ~/.bashrc' after editing the  '~/.bashrc' file, the environment will not be set.
        If you have any doubts, always 'source ~/.bashrc'

    There should be a ~/.bashrc file, but if not do:
        - 'cd'
        - 'ls- la | more'
            - this will show you which bash file you have
            - find it and edit that one instead


## Setting up the monitoring client service on the VM

Setting up the client service requires editing the monitoring.config file to your preferences. It configures the following options:

- slack: webhook url for slack
- discord: webhook url for discord
- timeout: the amount of seconds between requests to get data from the pis. By default it is set to 300 (5 minutes).
- pids_threshold: the highest amount of processes which should be running on a pi.
- mem_threshold: the largest amount of memory which should be in use on a pi.
- disk_threshold: the largest amount of disk space which should be taken up on a pi.
- cpu_threshold: the highest percent of CPU which should be in use by the pi.
- url: under the `[slack]` section, this should be a Slack webhook URL. under the `[discord]` section, this should be a Discord webhook.

1. Obtain a slack or discord webhook URL. For more information on how to set up webhooks, follow these instructions:
- [slack](https://api.slack.com/messaging/webhooks#getting_started)
- [discord](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)

2. Paste this webhook URL into its respective section in monitoring.config.

3. In the file monitoring_piman.sh, make the following change: on line 12, at the very end of the line, change `/path/to/hosts/file` to the actual path of your hosts file. Otherwise, the script will not be able to find your hosts file, and monitoring-client.py will not have any IPs of pis to iterate through and send data to.

4. Reload the systemd daemon, start the monitoring service, and check its status to verify it is working:

```
sudo systemctl daemon-reload
sudo systemctl start monitoring
sudo systemctl status monitoring
```

## Setting up the grafana.py service

1. Reload the systemd daemon, start the grafana (grafana.service which refers to grafana.sh and grafana.py, NOT the actual Grafana server) service, and check its status to verify it is working:

```
sudo systemctl daemon-reload
sudo systemctl start grafana
sudo systemctl status grafana
```

At this point, all three services should be set up: the monitoring server on the pis, the monitoring client on the VM, and the grafana data source on the VM.

## Installing and starting Grafana

1. Follow [these instructions]() to install and run Grafana on the VM. The instructions are for Debian/Ubuntu, since this is the OS which the VM runs.

2. To access the Grafana dashboard from your local computer, make sure you are connected to the VPN for the switch (you should already have openvpn set up by this point). Open a browser and navigate to the VM address that piman is running on: for example, `172.31.x.254:3000`, where x is your group number. The port is 3000 since this is Grafana's default server port.

3. Log in to the Grafana dashboard with username `admin` and password `admin`. You should now be able to view and modify your Grafana dashboard.

## Adding the SimpleJSON data source

1. Once you have logged in, hover over the Settings tab on the left, and click on "Data Sources". Click on "Add Data Source" to the right on the page which appears. Search for SimpleJSON and hit "Select". This will open its configuration page.

2. Find the HTTP section, and the first option should be URL. Set this to `127.0.0.1:8081` (this is the link to your grafana.py server.) Then, click Save and Test. If everything passed through normally, your grafana.py server should have received a request for the root index '/' and returned a 200 OK response.

## Making the dashboard

1. Create a new dashboard by clicking on the "plus" symbol in the menu to the left, and in the dropdown which appears, "Dashboard".

2. In the new dashboard, click "Add new panel". A panel will allow you to organize the monitoring data. This will open a configuration page with many options.  
  At the top you can edit the name of the panel.  
  The main option to look for is within the first tab under the graph which appears, called "Query". Here is where you will specify which timeseries you would like to display on the panel.  
  Simply click on 'select metric' and select a piece of data from one of the pis on the drop down menu.  
  Each query displays only one statistic for each pi, so naturally you will need to add more queries with the '+ query' button to display the same statistic but for the other pis.  

3. On the right side, under 'visualization' there are options to modify how the data is viewed. The options include using a graph or a gauge. By default, a graph is chosen. The 'display' option underneath 'visualization' shows how each query is shown, and the default is a line.

4. Directly on top of the graph there is a clock icon with a drop down menu where you can select the time frame that you want the data to be shown in. The icon with the down arrow on the farthest right gives the options of when to refresh the data.

5. For more information on how to set up your panel, consult [this link](https://grafana.com/docs/grafana/latest/panels/add-a-panel/). When you are finished with your panel, click save.

6. You can add more panels to display other combinations of features that you would like to monitor. You can do this by clicking on the icon with the bar graph and plus symbol inside of it.
