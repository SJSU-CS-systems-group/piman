# import click

from threading import Thread
from sys import argv

from dhcp import dhcp
from tcp import tcp
from tftp import tftp
from utility import power_cycle
from parse_config import config
import logging
import logging.config

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

#create logger using configuration
logging.config.fileConfig('./logging.conf')
logger = logging.getLogger('pimanlogger')

data_dir = "./install/boot"
tftp_port = 69
tcp_port = 3333
ip = config['server_address']
subnet_mask = config['subnet_mask']
mac_ip_file = "hosts.csv"
lease_time = 600
interface = config['interface']

def server():
    tftp_thread = Thread(target=tftp.do_tftpd, args=[data_dir, ip, tftp_port], name="tftpd")
    tftp_thread.start()

    dhcp_thread = Thread(target=dhcp.do_dhcp, args=[mac_ip_file, subnet_mask, ip, lease_time, interface], name="dhcpd")
    dhcp_thread.start()

    tcp_thread = Thread(target=tcp.do_tcp, args=[data_dir, tcp_port, ip], name="tcp")
    tcp_thread.start()

    tftp_thread.join()
    dhcp_thread.join()
    tcp_thread.join()


def restart(switch_address, ports):
    for port in ports:
        power_cycle.power_cycle(switch_address, port)


def reinstall(switch_address, port):
    with open("/tcp/reinstall.txt", "w") as f:
        network_addr = ip[:-1]
        f.write(network_addr+str(port))
    power_cycle.power_cycle(switch_address, port)


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
        if len(argv) < 3:
            exit_piman()
        restart(argv[2], argv[3:])
    elif argv[1] == "reinstall":
        if len(argv) < 3:
            exit_piman()
        reinstall(argv[2], argv[3])
