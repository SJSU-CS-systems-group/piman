# Table of Contents

[Setting Up Monitoring With Grafana and Prometheus](#Setting-Up-Monitoring-With-Grafana-and-Prometheus)  
[Overview](##Overview)  
[Preparation](##Preparation)  
[On The VM](##On-The-VM)  
[Setting up Node Exporter on the Pis](##Setting-up-Node-Exporter-on-the-Pis)  
[Setting up Prometheus with our DNS server](##Setting-up-Prometheus-with-our-DNS-server)  
[Installing and starting Grafana](##Installing-and-starting-Grafana)  
[Adding the Prometheus data source](##Adding-the-Prometheus-data-source)  
[Making the dashboard](##Making-the-dashboard)  

# Setting Up Monitoring With Grafana and Prometheus 

## Overview

Prometheus is a data source which the Grafana dashboard will use. It will be able to retrieve data from the node exporters on each pi and connect to our DNS server, which returns SRV records of all of our pis.

The node exporter on every pi is a server which, when queried by Prometheus, will retrieve system data from the pi. The data currently collected includes:
* CPU load
* memory usage
* disk usage
* number of processes running
* temperature

Once retrieved, the node exporter will respond to the query by sending that data back to Prometheus. Prometheus will then expose that data to Grafana. 

The first step is getting Node Exporter (which will be running on a rootfs file provided by Ben) on all of the pis, running on port 9100. Then, Prometheus must be set up on the VM, running on port 9090. We must install Grafana itself on the VM and then set up Grafana with a Prometheus data source.
Once its service is started, Grafana will run a web server on port 3000. Through this server is how the dashboard and data panels will be set up. 

The following sections will explain the steps to set up monitoring in detail.

## Preparation

The first step is to update all the pis' package repositories, install all dependencies, make all necessary directories, and copy files to the right locations.

## On the VM

1. Clone the piman directory into /usr/local:

```
cd /usr/local 
sudo git clone https://github.com/SJSU-CS-systems-group/piman.git
```

This will make sure that /usr/local/piman/monitoring is a path which exists on your system.

2. Copy the grafana.service files to /etc/systemd/system:

```
sudo cp grafana.service /etc/systemd/system
```

3. Install python dependencies:

```
sudo pip3 install requests
```

## Setting up Node Exporter on the Pis


1. Download the rootfs file that Ben will provide. 
2. Replace the new rootfs with the old rootfs in your /install/boot directory on the VM. rootfs will run node exporter. 
3. Reinstall all of your pis so that every pi will have node exporter on them. 

From your /build directory, you can reinstall a pi with: 

```
sudo python3 piman.pyz reinstall 172.16.<groupnumber>.129 1 <portname>
```

4. ssh into the pi and check if node exporter was installed. 

```
ssh pi@172.16.<groupnumber>.<portname>
```

After logging into the pi, you should find a node_exporter.service file in /usr/local/bin directory if node_exporter was successfully installed. 
A node_exporter.service file should be located under /etc/systemd/system 

5. Start node exporter and ensure everything is running correctly.
```
sudo systemctl daemon-reload
sudo systemctl start node_exporter 
sudo systemctl status node_exporter
```

## Setting up Prometheus with our DNS server 
1. [Download the latest release](https://prometheus.io/download/) of Prometheus for your platform, then extract it: 

```
tar xvfz prometheus-2.27.0.linux-amd64.tar.gz 
cd prometheus-2.27.0.linux-amd64
```

2. The Prometheus server is a single binary called prometheus (or prometheus.exe on Microsoft Windows). We can run the binary and see help on its options by passing the --help flag.

```
./prometheus --help
```

3. To start Prometheus with our newly created configuration file, change to the directory containing the Prometheus binary and run:

```
./prometheus --config.file=prometheus.yml
```

Prometheus should start up. You should be able to browse to a status page about itself at http://172.27.x.128:9090 where x is your city number. 
You can also verify that Prometheus is serving metrics about itself by navigating to its own metrics endpoint: http://172.27.x.128:9090/metrics where x is your city number. 
4. Setup the configuration file.
Prometheus configuration is YAML. The Prometheus download comes with a sample configuration in a file called prometheus.yml that is a good place to get started. 

```
sudo nano prometheus.yml 
``` 

Edit the yml file:

```
# my global config
global:
  scrape_interval:     15s # Set the scrape interval to every 15 seconds. Default is every 1 minute.

scrape_configs:
  - job_name: 'node'
    dns_sd_configs:
    - names:
     -'metrics.x.cs158b' #x is your city name 
```
 
This setup will allow prometheus to get SRV records from your DNS server so that we don't have to preconfigure targets. 
5. Set up a service file. 

```
sudo nano /etc/systemd/system/prometheus.service 
``` 

Edit the service file: 

```
[Unit]
Description=Raspberry Pi Monitoring with Prometheus
After=network.target

[Service]
User=root
Group=sudo
Type=simple
WorkingDirectory=<path to prometheus-2.27.0.linux-amd64> 
ExecStart=<path to prometheus-2.27.0.linux-amd64/prometheus> 
Restart=on-failure
RestartSec=15

[Install]
WantedBy=multi-user.target
```

Ensure that prometheus is setup correctly: 

```
sudo systemctl daemon-reload
sudo systemctl start prometheus
sudo systemctl status prometheus
```

6. Edit resolv.conf to point to your DNS nameserver. 

``` 
cd /etc/resolv.conf 
```   
Changes to /etc/resolv.conf are not permanent. To get around this, make sure that the resolvconf app is installed on the VM

```
sudo apt-get install resolvconf
```
Next, navigate to the resolveconf service files

```
cd /etc/resolvconf/resolv.conf.d
```
Edit the file called head to include nameserver 127.0.0.1 under the comment line in the file
```
#### COMMENTS ####
### COMMENTS ####
### COMMENTS ####

nameserver 127.0.0.1
```
This will place the localhost address at the top of /etc/resolv.conf everytime the VM is rebooted.

## Installing and starting Grafana

1. Follow [these instructions](https://grafana.com/docs/) to install and run Grafana on the VM. The instructions are for Debian/Ubuntu, since this is the OS which the VM runs.

2. To access the Grafana dashboard from your local computer, make sure you are connected to the VPN for the switch (you should already have openvpn set up by this point). Open a browser and navigate to the VM address that piman is running on: for example, `172.27.x.128:3000`, where x is your group number. The port is 3000 since this is Grafana's default server port.

3. Log in to the Grafana dashboard with username `admin` and password `admin`. You should now be able to view and modify your Grafana dashboard.

## Adding the Prometheus data source

1. Once you have logged in, hover over the Settings tab on the left, and click on "Data Sources". Click on "Add Data Source" to the right on the page which appears. Search for Prometheus and hit "Select". This will open its configuration page.

2. Find the HTTP section, and the first option should be URL. Set this to `172.27.x.128:9090` where x is your city number. 
3. The second option under HTTP should be Access. Set it to "Server". Then, click Save and Test.

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

6. For each query, you will have a Metrics option. Select the metric that you want the graph to display (for example, "node_cpu_seconds_total"). 

7. You can add more panels to display other combinations of features that you would like to monitor. You can do this by clicking on the icon with the bar graph and plus symbol inside of it.


