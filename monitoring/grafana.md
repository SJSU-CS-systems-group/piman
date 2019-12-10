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