import threading
from flask import Flask, escape, request, render_template, jsonify
import click
import os.path

hosts_csv_path = "../hosts.csv"
config_path = "../.yaml"
org_name = ""

#remaps .pyz to .app
def get_flask_path():
    flask_path = os.path.dirname(os.path.abspath(__file__))
    if ".pyz" in flask_path:
        flask_path = flask_path[0:flask_path.find(".pyz")]
        flask_path += ".app/config_ui/"
    print(flask_path)
    return flask_path

app = Flask(__name__, root_path=get_flask_path())

@app.route('/')
def home():
    return render_template("home.html", city=org_name)


@app.route('/hosts-csv')
def read_hosts_csv():
    return render_template("hosts_csv.html")


@app.route('/config')
def read_config():
    return render_template("config.html")


@app.route('/hosts-csv', methods=['POST'])
def hosts_csv_form_post():
    listOfInputsMac = request.form.getlist('inputsMac')
    listOfInputsIp = request.form.getlist('inputsIp')
    listOfInputsName = request.form.getlist('inputsName')
    listOfInputsTimestamp = request.form.getlist('inputsTimestamp')
    with open(hosts_csv_path, "w") as f:
        for i in range(len(listOfInputsMac)):
            if listOfInputsMac[i] == "" and listOfInputsIp[i] == "" and listOfInputsName[i] == "" and listOfInputsTimestamp[i] == "":
                continue
            if listOfInputsMac[i]:
                f.write(listOfInputsMac[i])
            f.write(";")
            if listOfInputsIp[i]:
                f.write(listOfInputsIp[i])
            f.write(";")
            if listOfInputsName[i]:
                f.write(listOfInputsName[i])
            f.write(";")
            if listOfInputsTimestamp[i]:
                f.write(listOfInputsTimestamp[i])
            f.write("\n")
    return render_template("hosts_csv.html")


@app.route('/config', methods=['POST'])
def config_form_post():
    listOfInputs = request.form.getlist('inputs')
    listOfSwitches = request.form.getlist('inputsSwitch')
    numOfPis = request.form.getlist('inputsSwitchLen')
    listOfPis = request.form.getlist('inputsPi')
    with open(config_path, "w") as f:
        f.write("private_number: " + listOfInputs[0] + "\n")
        f.write("server_address: " + listOfInputs[1] + "\n")
        f.write("subnet_mask: " + listOfInputs[2] + "\n")
        f.write("switch_count: " + str(len(listOfSwitches)) + "\n")
        f.write("switches:\n")
        currSwitch = 0
        currPi = 0
        for switch in listOfSwitches:
            f.write("  - switch_" + str(currSwitch) +
                    "_address: " + switch + "\n")
            f.write("    pi_addresses:" + "\n")
            for num in range(0, int(numOfPis[currSwitch])):
                f.write("      - " + listOfPis[currPi] + "\n")
                currPi += 1
            currSwitch += 1
    return render_template("config.html")


@app.route('/get_hosts_csv', methods=['GET'])
def get_hosts_csv():
    if os.path.isfile(hosts_csv_path) == False:
        print("Host csv not found, generating new file")
        with open(hosts_csv_path, "w") as f:
            f.write("")
    with open(hosts_csv_path) as f:
        hosts_csv_file_read = f.readlines()
    return jsonify(hosts_csv_file_read)


@app.route('/get_config', methods=['GET'])
def get_config():
    config_file_read = {}
    if os.path.isfile(config_path) == False:
        print("Config yaml not found, generating new file")
        with open(config_path, "w") as f:
            f.write("private_number: \n")
            f.write("server_address: \n")
            f.write("subnet_mask: \n")
            f.write("switch_count: \n")
            f.write("switches:\n")
            f.write("  - switch_0_address: \n")
            f.write("    pi_addresses:" + "\n")
            f.write("      - \n")
    fileHandler = open(config_path, "r")
    while True:
        # Get next line from file
        line = fileHandler.readline()
        key, value = line.partition(":")[::2]
        key = key.replace("-", "")
        value = value.replace("-", "")
        switches_arr = []
        if not line:
            break
        if "switches" in key:
            while True:
                temp_line = fileHandler.readline()
                if "switch" in temp_line:
                    val1, val2 = temp_line.partition(":")[::2]
                    val1 = val1.replace("-", "")
                    val2 = val2.replace("-", "")
                    tempDict = {}
                    tempDict[val1.strip()] = val2.strip()
                    temp_line = fileHandler.readline()
                    val1, val2 = temp_line.partition(":")[::2]
                    val1 = val1.replace("-", "")
                    val2 = val2.replace("-", "")
                    tempDict[val1.strip()] = []
                    while True:
                        last_pos = fileHandler.tell()
                        pi_line = fileHandler.readline()
                        if "switch" in pi_line or not pi_line:
                            fileHandler.seek(last_pos)
                            break
                        pi_line = pi_line.replace("-", "")
                        tempDict["pi_addresses"].append(pi_line.strip())
                    switches_arr.append(tempDict)
                config_file_read["switches"] = switches_arr
                if not temp_line:
                    break
        else:
            config_file_read[key.strip()] = value.strip()
    fileHandler.close()
    return jsonify(config_file_read)


'''
@click.command()
@click.option('--name', prompt='Your Organization',
              help='The name of your organization.')
@click.option('--configpath', prompt='Path of config (.yaml) file',
              help='The path to the config file from the current working path.')
@click.option('--hostcsvpath', prompt='Path of hosts.csv file',
              help='The path to the config file from the current working path.')
'''


def start(name, configpath, hostcsvpath):
    global org_name
    org_name = name
    global config_path
    config_path = configpath
    global hosts_csv_path
    hosts_csv_path = hostcsvpath
    app.run()


if __name__ == "__main__":
    start()
