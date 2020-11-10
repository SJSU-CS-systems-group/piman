#!/usr/bin/python3

"""
Here are some useful information for interactiong with grafana.py
through JSON.
Simple JSON Datasource:
https://github.com/grafana/simple-json-datasource
Grafana Simple JSON plug-in page:
https://grafana.com/grafana/plugins/simpod-json-datasource
"""

import requests
import json
import click
import datetime

def check(server, port):
    """check
    Check if the connection has been established fine
    """
    try:
        r = requests.get(f'http://{server}:{port}/')
    except requests.exceptions.ConnectionError as e:
        # response with error -> exit
        return 'Connection failed\n\n{}\n\nCheck the IP and port, make sure grafana.py is running'.format(e)
    return r.text


def query(server, port, target, time_range, less=None):
    """query
    query the monitoring data from the grafana.py
    Args:
        target: the target to query from
        time_range: the time range of the returning data
        less: option to show only the first 10 data(not implemented)
    """
    hr = "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
    click.echo(hr)
    click.echo('\tTarget: {}\n\tTime Range: {}'.format(target, time_range))
    click.echo(hr)
    click.echo('Fetching data ...')

    t_from_str = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    t_to = datetime.datetime.now() + datetime.timedelta(minutes=(time_range))
    t_to_str = t_to.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    payload = {
        "range": {
            "from": t_from_str,
            "to": t_to_str,
        },
        "targets": [
            {"target": target},
        ]
    }
    try:
        re = requests.post(f'http://{server}:{port}/query', json=payload)
    except requests.exceptions.ConnectionError as e:
        # response with error -> exit
        return 'Connection failed\n\n{}\n\nCheck the IP and port, make sure grafana.py is running'.format(e)

    click.echo('Data recieved')
    click.echo('Data processing ...')
    json_data = re.json()[0]
    raw_data_list = json_data['datapoints']
    re_text = [hr, "\tData List:\n", hr]
    if less:
        for line in raw_data_list[:10]:
            date = datetime.datetime.fromtimestamp(line[1]/1000.0)
            re_text.append('\t{} -- {}\n'.format(date.strftime('%c'), line[0]))
    else:
        for line in raw_data_list:
            date = datetime.datetime.fromtimestamp(line[1]/1000.0)
            re_text.append('\t{} -- {}\n'.format(date.strftime('%c'), line[0]))
    return "".join(re_text)

def search(server, port):
    """search
    Send search request to grafana.py.
    Bashed on the current implementation of grafana.py, 
    search will always returns a list of all targets.
    """
    # start a sub routine getting searching input

    # fetch all targets. Targets are the names to query for
    click.echo('Getting list of targets ...')
    try:
        re = requests.post(f'http://{server}:{port}/search')
    except requests.exceptions.ConnectionError as e:
        # response with error -> exit
        return 'Connection failed\n\n{}\n\nCheck the IP and port, make sure grafana.py is running'.format(e)

    tar_list = eval(re.text)
    hr = "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
    re_text = [hr,"\tTarget List:\n", hr]
    [re_text.append("\t{}\n".format(tar)) for tar in tar_list]
    re_text.append(hr)
    return "".join(re_text)




def help_page():
    return ''.join(['       ?/help - Get helping message.\n',
                    '       q/quit - Quit Grafana CLI.\n',
                    '       c/check - Check connection.\n',
                    '       search - Returning available metrics when invoked.\n',
                    '       query - Returning metrics based on input.\n'])

@click.command()
@click.option('--server', prompt='Server IP', help='The IP where the grafana is running')
@click.option('--port', prompt='port', help='The port grafana.py is running on')
def main(server, port):
    click.echo('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    click.echo('                Welcome to Monitoring CLI\n')
    click.echo('    This is a command line interface interacting with grafana.py.')
    click.echo('    This tool will perform simple REST interaction between grafan-')
    click.echo('     a.py to check if the Grafana service is running as expectied.\n')
    click.echo('    Type ?/help for help')
    click.echo('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')

    while True:
        op = input('> ')

        if op == '?' or op == 'help':
            help_msg = help_page()
            # print the help page
            click.echo(help_msg)
        elif op == 'q' or op == 'quit':
            click.echo('Exiting Grafana CLI ...')
            break
        elif op == 'c' or op == 'check':
            re = check(server, port)
            click.echo(re)
        elif op == 'search':
            re = search(server, port)
            click.echo(re)
        elif op == 'query':
            target = input('Target name(must from target list, format: "some target"): ')
            # if no target -> exit
            if not target:
                click.echo('Target cannot be empty.')
                continue
            time_range = input('Time Range(default 5 min): ')
            if not time_range:
                # default to 5 min
                time_range = 5
            time_range = int(time_range)
            re = query(server, port, target, time_range)
            click.echo(re)
        else:
            click.echo(f'Invalid input {op}, type ?/help for help')

if __name__ == '__main__':
    main()
