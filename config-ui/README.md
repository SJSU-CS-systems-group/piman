# UI for configuration and hosts.csv
This is a simple Python server-side web application which helps users modify the configuration .yaml and hosts.csv.

## Setup
This setup should only be needed if you are looking to run the web application by itself.

1. Install Flask, the python web application framework: 'sudo apt install python3-flask'.  'pip3 install flask' may also work as well if you have pip3.
2. In the /config-ui/ directory, run the following command to start the server: 'python3 web_ui.py'.  This will prompt users for their city name, config path, and hosts.csv path.  'env FLASK_APP=web_ui.py flask run' will also run the server, but uses the default hardcoded configuration.

That's it.

## SSH Tunneling

Sometimes PiMan runs on a VM, making it difficult to access the website directly.  Use SSH tunneling instead.
- On one terminal: SSH into your city and go to /config-ui/.  Start the webserver, as stated in Setup #2.
- On another terminal: Execute this command: 'ssh -L 8080:localhost:5000 dubai' but replace ‘dubai’ with your city’s name or endpoint.
- You should now be able to connect to the webserver on your ssh client by going to 'localhost:8080' in your browser.

## More Information

By default, this webserver will modify the files .yaml and hosts.csv in the root directory of PiMan.  Configurations refers to .yaml by default.  These files are regularly checked in order to dynamically update the UI.  If these files do not exist, they will be automatically generated with some placeholder information.