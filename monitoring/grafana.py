import os
from sys import argv
from datetime import datetime
from calendar import timegm
from bottle import (Bottle, HTTPResponse, run, request, response,
                    json_dumps as dumps)
app = Bottle()
log_path = ''
DATA = {}


def parse():
    DATA.clear()
    try:
        f = open(log_path, "r")
        contents = f.read().split("\n \n")
        if '' in contents:
            contents.remove('')
        for pi_info in contents:
            pi = pi_info.split("\n")
            pi_ip = pi[0].split('@')[1]
            ts = datetime.strptime(pi[0].split(' -')[0], '%a %b %d %H:%M:%S %Y')
            time = ts.timestamp() * 1000
            try:
                #The Arrays use negative indicies so that that, if the pi goes above threshold or has to display an error message,
                #Grafana will still be able to receive the numbers and update the dashboards.
                if "CPU" not in pi_info:
                    insert_data(pi_ip + " CPU", time, 0)
                else:
                    cpu_load = float(pi[-5].replace("CPU load: ", "").replace(" ", ""))
                    insert_data(pi_ip + " CPU", time, cpu_load)

                if "RAM" not in pi_info:
                    insert_data(pi_ip + " Ram", time, 0)
                else:
                    ram = float(pi[-4].replace("RAM usage: ", "").replace(" ", ""))
                    insert_data(pi_ip + " Ram", time, ram)

                if "Disk" not in pi_info:
                    insert_data(pi_ip + " Disk Usage", time, 0)
                else:
                    disk_usage = float(pi[-3].replace("Disk usage: ", "").replace(" ", ""))
                    insert_data(pi_ip + " Disk Usage", time, disk_usage)

                if "PID" not in pi_info:
                    insert_data(pi_ip + " PIDs", time, 0)
                else:
                    pids = int(pi[-2].replace("# of PIDs: ", "").replace(" ", ""))
                    insert_data(pi_ip + " PIDs", time, pids)

                if "Temperature" not in pi_info:
                    insert_data(pi_ip + " Temperature", time, 0)
                else:
                    temp = float(pi[-1].replace("Temperature: ", "").replace(" F", "").replace(" ", ""))
                    insert_data(pi_ip + " Temperature", time, temp)

            except Exception as e:
                print(e)

        return True

    except:
        print("Monitoring Log file not found, make sure log_path points to monitor.log file")
        return False


def insert_data(field, time, value):
    if field not in DATA:
        DATA[field] = {time: value}
    else:
        DATA[field][time] = value


def convert_to_time_ms(timestamp):
    return 1000 * timegm(
        datetime.strptime(
            timestamp, '%Y-%m-%dT%H:%M:%S.%fZ').timetuple())


def create_data_points(data, start, end):
    lower = convert_to_time_ms(start)
    upper = convert_to_time_ms(end)

    times = list(data.keys()) + [lower, upper]

    results = []
    to_enter = 0
    for time in sorted(times):
        if time in list(data.keys()):
            results.append([to_enter, time - 1])
            results.append([data[time], time])
            to_enter = data[time]
        else:
            results.append([to_enter, time])

    print(results)
    return results


@app.hook('after_request')
def enable_cors():
    print("after_request hook")
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = \
        'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'


@app.route("/", method=['GET', 'OPTIONS'])
def index():
    return "OK I'M READY"


@app.post('/search')
def search():
    return HTTPResponse(body=dumps(list(DATA.keys())),
                        headers={'Content-Type': 'application/json'})


@app.post('/query')
def query():
    print(request.json)
    try:
        body = []
        start, end = request.json['range']['from'], request.json['range']['to']
        for target in request.json['targets']:
            name = target['target']
            parse()
            datapoints = create_data_points(DATA[name], start, end)
            print(datapoints)
            body.append({'target': name, 'datapoints': datapoints})

        body = dumps(body)
    except:
        print("Something Went Wrong")

    return HTTPResponse(body=body,
                        headers={'Content-Type': 'application/json'})


if __name__ == '__main__':
    if len(argv) > 1:
        log_path = argv[1]

    if parse():
        run(app=app, host='', port=8081)
