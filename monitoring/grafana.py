from sys import argv
from datetime import datetime
from calendar import timegm
from bottle import (Bottle, HTTPResponse, run, request, response,
                    json_dumps as dumps)

app = Bottle()

log_path = "logs/monitor.log"
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
            time = int(float(pi[0].split(' -')[0]) * 1000)
            cpu_load = float(pi[3].replace("CPU load: ", "").replace(" ", ""))
            ram = float(pi[4].replace("RAM usage: ", "").replace(" ", ""))
            disk_usage = float(pi[5].replace("Disk usage: ", "").replace(" ", ""))
            pids = int(pi[6].replace("# of PIDs: ", "").replace(" ", ""))
            temp = float(pi[7].replace("Temperature: ", "").replace(" Celsius", "").replace(" ", ""))

            if pi_ip + " CPU" not in DATA:
                DATA[pi_ip + " CPU"] = {time: cpu_load}
            else:
                DATA[pi_ip + " CPU"][time] = cpu_load

            if pi_ip + " Ram" not in DATA:
                DATA[pi_ip + " Ram"] = {time: ram}
            else:
                DATA[pi_ip + " Ram"][time] = ram

            if pi_ip + " Disk Usage" not in DATA:
                DATA[pi_ip + " Disk Usage"] = {time: disk_usage}
            else:
                DATA[pi_ip + " Disk Usage"][time] = disk_usage

            if pi_ip + " PIDs" not in DATA:
                DATA[pi_ip + " PIDs"] = {time: pids}
            else:
                DATA[pi_ip + " PIDs"][time] = pids

            if pi_ip + " Temperature" not in DATA:
                DATA[pi_ip + " Temperature"] = {time: temp}
            else:
                DATA[pi_ip + " Temperature"][time] = temp

        return True
    except:
        print("Monitoring Log file not found, make sure log_path points to monitor.log file")
        return False


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
    return "OK"


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
        run(app=app, host='grafana', port=3333)