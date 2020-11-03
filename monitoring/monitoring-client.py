"""
This script runs on the manager pi
it will poll the slave pis via HTTP GET request to port 3000
"""
import json
import time
import requests
import configparser
from sys import argv
import sys
sys.path.append(".")
from piman import logger
from parse_config import config

ips = []

for list in config['switches']:
    for addr in list['pi_addresses']:
        ips.append(addr)

monitor_config = configparser.ConfigParser()
log_path = ""

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
    return "---- From {} ---- \n Time: {} \n CPU load: {} \n RAM usage: {} \n Disk usage: {} \n # of PIDs: {} \n Temperature: {} C \n".format(
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

    filepath = 'hosts.csv'
    with open(filepath) as hosts:

    # Main loop, polls the 9 pis then waits
        while True:
            line = hosts.readline()
            if line == '': # skip empty lines
                continue
            ip = line.split(';')[1]
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


if __name__ == "__main__":
    if len(argv) < 2: 
        print("Please give path to config file and/or log path")

    # read config
    monitor_config.read(argv[1])
    log_path = argv[2] if len(argv) == 3 and argv[2] else "logs/monitor.log"

    _main()
