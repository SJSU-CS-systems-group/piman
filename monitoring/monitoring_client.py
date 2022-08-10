"""
This script runs on the manager pi
it will poll the slave pis via HTTP GET request to port 3000
This script also has a method start_from_piman which is used to run client from piman
"""
import json
import time
import requests
import configparser
from sys import argv

monitor_config = configparser.ConfigParser()
log_path = "logs/monitor.log"
hosts_path = "hosts.csv"

def alert(data):
    print_to_file(data)
    if monitor_config['DEFAULT']['discord']:
        url = monitor_config['DEFAULT']['discord']
        info = {'username': 'piman', 'content': 'Alert:', 'embeds': []}
        info["embeds"].append({'description': data})
        try:
            r = requests.post(url, data=json.dumps(info), headers={'Content-type': 'application/json'})
        except Exception as e:
            print_to_file("Unable to send alert - {}".format(e))
        print_to_file("Alerting (discord) - {}: {}\n".format(r.status_code, r.reason))
    if monitor_config['DEFAULT']['slack']:
        url = monitor_config['DEFAULT']['slack']
        try:
            r = requests.post(url, data=json.dumps({'text':'{}'.format(data)}), headers={'Content-type': 'application/json'})
        except Exception as e:
            print_to_file("Unable to send alert - {}".format(e))
        print_to_file("Alerting (slack) - {}: {}\n".format(r.status_code, r.reason))


def pretty_stats(ip, event):
    return "---- From {} ---- \n Time: {} \n CPU load: {} \n RAM usage: {} \n Disk usage: {} \n # of PIDs: {} \n Temperature: {} F \n".format(
            ip,
            event['time'], 
            event['cpu_percent'],
            event['memory_percent'],
            event['disk_percent'],
            event['num_pids'],
            event['temp'],
        )


def get_status(pi_ip):
    get_string = 'http://{}:3000/event/'.format(pi_ip)
    r = requests.get(get_string, timeout=10)
    return r


def check_response(response_dict, pi):
    if response_dict['cpu_percent'] > float(monitor_config['DEFAULT']['cpu_threshold']):
        alert("CPU beyond threshold on pi@{}".format(pi))
    if response_dict['memory_percent'] > float(monitor_config['DEFAULT']['mem_threshold']):
        alert("Memory beyond threshold on pi@{}".format(pi))
    if response_dict['disk_percent'] > float(monitor_config['DEFAULT']['disk_threshold']):
        alert("Disk Usage beyond threshold on pi@{}".format(pi))
    if response_dict['num_pids'] > int(monitor_config['DEFAULT']['pids_threshold']):
        alert("Number of PID's beyond threshold on pi@{}".format(pi))
    if response_dict['temp'] > float(monitor_config['DEFAULT']['temperature_threshold']):
        alert("Temperature beyond threshold on pi@{}".format(pi))

def print_to_file(data):
    with open(log_path, "a") as f:
        f.write("{} - {} \n".format(time.ctime(), data))


def _main():
    timeout = int(monitor_config['DEFAULT']['timeout'])

    hostips = []
    try:
        with open(hosts_path, "r") as hostfile:
            hosts = hostfile.readlines()
            for line in hosts:
                hostips.append(line.split(';')[1])
    except IOError as ioe:
        exit("Hosts file not found. Please specify correct path.")
    # Main loop, polls the 9 pis then waits
    while True:
        for ip in hostips:

            time.sleep(1) # to avoid 429 - too many requests error
            r = None
            try:
                print_to_file("Sending HTTP-GET to pi@{}".format(ip))
                r = get_status(ip)
                r.raise_for_status()  # Raises exceptions if the response code is over 400 aka bad response
            except requests.exceptions.Timeout:
                # Couldn't reach the server
                alert("Timeout when trying to reach pi@{}".format(ip))
            except requests.exceptions.RequestException:
                alert("Exception when trying to reach pi@{}".format(ip))
            if r:
                r_json = r.json()
                check_response(r_json, ip)
                print_to_file(pretty_stats(ip, r_json))
        time.sleep(timeout)

def start_from_piman():
    monitor_config.read("monitoring.config")
    _main()

if __name__ == "__main__":
    if len(argv) < 3: 
        print("Please give path to config file, log path, and/or hosts file")

    # read config
    monitor_config.read(argv[1])
    log_path = argv[2] if len(argv) == 3 and argv[2] else "logs/monitor.log"
    hosts_path = argv[3] if len(argv) == 4 and argv[3] else exit("Log file or Host file not found.")

    _main()
