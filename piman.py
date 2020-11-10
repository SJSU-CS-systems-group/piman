import logging
import logging.config
import os
from zipfile import ZipFile
import io
import time
import signal

# create the logger before doing imports since everyone is going
# to use them
local_logfile = './logging.conf'
if os.path.isfile(local_logfile):
    logging.config.fileConfig(local_logfile)
else:
    zipfile = os.path.dirname(__file__)
    with ZipFile(zipfile) as z:
        fd = z.open("logging.conf", mode='r')
        # convert to a string
        confstr = fd.read().decode()
        logging.config.fileConfig(io.StringIO(confstr))

#create logger using configuration
logger = logging.getLogger('pimanlogger')

from threading import Thread
from sys import argv

from config_ui import web_ui
from dhcp import dhcp
from tcp import tcp
from tftp import tftp
from utility import power_cycle
from utility import mac_mapper
from logger import logger
from parse_config import config
import ntpserver

'''
piman.py

Attributes:
-----
data_dir : str
    the directory of files needed for pis to boot
tftp_port : int
    tftp use udp port 69 to establish network connection
tcp_port : int
    tcp port number for tcp to establish network connection
ip : str
    network ip address of pis and ip address of the router
subnet_mask : str
    subnet mask for the ip address of pis
switch_address : str
    ip address of the switch that connect pis
mac_ip_file : str
    address of the file that save the mac address of pis and its ip address
    
Methods
-----
server()
    Start tftp, dhcp, tcp connection between server and pis
restart(switch_address, port)
    to restart the specific pi
reinstall(switch_address, port)
    to reinstall a specific pi
exit_piman()
    to exit piman
    
'''

data_dir = "./install/boot"
tftp_port = 69
tcp_port = 3333
ip = config['server_address']
subnet_mask = config['subnet_mask']
mac_ip_file = "hosts.csv"
lease_time = 600
interface = config['interface']


def server():
    config_ui_thread = Thread(target=config_ui, args=[
                              "", "./piman.yaml", "./hosts.csv"], name="config_ui")
    config_ui_thread.start()

    tftp_thread = Thread(target=tftp.do_tftpd, args=[
                         data_dir, ip, tftp_port], name="tftpd")
    tftp_thread.start()

    dhcp_thread = Thread(target=dhcp.do_dhcp, args=[
                         mac_ip_file, subnet_mask, ip, lease_time, interface], name="dhcpd")
    dhcp_thread.start()

    tcp_thread = Thread(target=tcp.do_tcp, args=[
                        data_dir, tcp_port, ip], name="tcp")
    tcp_thread.start()

    ntp_thread = Thread(target=ntpserver.do_ntp())
    ntp_thread.start()

    signal.pthread_kill(config_ui_thread.ident, 15) # 15 = sigterm
    signal.pthread_kill(tftp_thread.ident, 15)
    signal.pthread_kill(dhcp_thread.ident, 15)
    signal.pthread_kill(tcp_thread.ident, 15)
    # ntp_thread does not need to be killed. ntpserver takes control of the terminal
    # when it is run, so after it is closed by a keyboard interrupt, the above
    # lines run closing the rest of the threads. ntp_thread will already be stopped


def restart(switch_address, interface, ports):
    for port in ports:
        power_cycle.power_cycle(switch_address, interface, port)


def reinstall(switch_address, interface, port):
    with open("reinstall.txt", "w") as f:
        network_addr = ip[:7] + str(interface) + "." + str(port)
        f.write(network_addr)
    power_cycle.power_cycle(switch_address, interface, port)
    
def mapper(switch_address,interface, port, file):
    for portNum in port:
        power_cycle.power_cycle(switch_address,interface, portNum)
    time.sleep(30)
    mac_mapper.mac_mapper(file)

def config_ui(name, config_path, hosts_csv_path):
    web_ui.start(name, config_path, hosts_csv_path)

def exit_piman():
    logger.error("Insufficient amount of arguments")
    exit(1)

if __name__ == "__main__":
    args = "Arguments: "
    for a in argv:
        args += a + " "
    logger.info(args)

    if len(argv) < 2:
        exit_piman()

    if argv[1] == "server":
        server()
    elif argv[1] == "restart":
        if len(argv) < 5:
            exit_piman()
        restart(argv[2], argv[3],argv[4])
    elif argv[1] == "mapper":
        if len(argv) < 5:
            exit_piman()
        mapper(argv[2],argv[3],argv[4])
    elif argv[1] == "reinstall":
        if len(argv) < 5:
            exit_piman()
        reinstall(argv[2], argv[3], argv[4])
    elif argv[1] == "config":
        config_ui(argv[2], argv[3], argv[4])

