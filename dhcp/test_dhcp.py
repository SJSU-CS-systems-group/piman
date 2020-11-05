import unittest
from multiprocessing import Process
import dhcp
from random import randint
import random
import sys
import socket
from .listener import *
import time
import uuid

'''
[important] how to test dhcp
there is some changes in __main__.py to run dhcp test as a command of pyz file
need make zip app first
then run: python3 build/piman.pyz run-test
this can fix the dhcp listener import error

DHCP assigns IP to pis
Test if DHCP assign the right IP to the request client? 
    no duplicated ip
    can access to the client

[1 host for 1 test routine]
1. mac must exits in hosts.csv
    generate a random test mac
    use mac to create a host
    add the host into hosts.csv
2. 1 test for no assigned ip
    make discovery message
3. 1 test for assigned ip

DHCP DISCOVER -> 
<- DHCP OFFER
DHCP REQUEST ->
<- DHCP PACK
DHCP RELEASE ->

'''


class dhcp_tests(unittest.TestCase):
    # server set up
    server_ip = '127.0.0.1'  # using local host as server
    subnet_mask = '255.255.255.0'
    host_file = 'hosts.csv'
    DHCP_config = ''

    # client host set up
    client_mac = ''
    client_ip = ''
    transaction_id = 0
    testHost = ''
    request_ip = 0

    test_packet_hex = "dca632b023c3a36e27a5ebf60800450001adcd4440004011014eac100980ac10090d004300440199142402010600d09fd9070000000000000000ac10090dac10098000000000dca632b023c300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000638253630104ffffff000304ac1009803c09505845436c69656e74420c3137322e31362e392e313238430c626f6f74636f64652e62696e0604080808082a04ac1009803304000002583501023604ac1009803d06dca632b023c33a04000054603b04000093a81c04ac1009ff611100525069341431d00032b023c3d80092e02b230601030a0400505845091700001452617370626572727920506920426f6f74202020ffff"


    # test udp_checksum function
    def test_udp_checksum(self):
        bootp = bytes.fromhex(self.test_packet_hex[84:])
        sip = "172.16.9.128"
        dip = "172.16.9.13"

        checksum = dhcp.dhcp.udp_checksum(sip, dip, bootp)

        correct_checksum = b'\x14\x24'
        self.assertEqual(correct_checksum, checksum)

    # for test cvs db
    def getRandomIP(self):
        arr = ['127','0','0']
        arr.append(str(randint(0, 255)))
        return '.'.join(arr)

    # generate random mac address every time start test
    def getRandomMAC(self):
        arr = []
        for i in range(6):
            mac_part = str(hex(randint(0, 255)))
            mac_part = mac_part[2:]
            if len(mac_part)<2:
                mac_part = '0'+mac_part
            arr.append(mac_part)
        tmp_mac = ':'.join(arr)
        return tmp_mac

    def create_test_host(self):
        # generated a random test mac, use that mac to create a host
        self.client_mac = self.getRandomMAC()
        self.client_ip = self.getRandomIP()
        self.testHost = dhcp.dhcp.Host(self.client_mac, self.client_ip, 'testHost', 0)
        # self.check_CSVDatabase()
        return self.testHost

    def create_HostDatabase(self):
        # Test if a new mac and is added to host.csv
        # create csv database
        test_db = dhcp.dhcp.HostDatabase(self.host_file)
        test_db.add(self.create_test_host())
        # need assert in csvdatabase to check if add mac to host

    def check_CSVDatabase(self):
        # Test if a new host and is added to host.csv
        # create csv database
        test_db = dhcp.dhcp.CSVDatabase(self.host_file)
        db_content = test_db.all()
        print("do csv db test")
        self.assertEqual(self.client_mac, db_content[-1][0])
        self.assertEqual(self.client_ip, db_content[-1][1])
        # print(test_db.all())

    def create_DHCPServerConfiguration(self):
        # sever configuration set up
        self.DHCP_config = dhcp.dhcp.DHCPServerConfiguration(self.server_ip, self.subnet_mask)
        self.DHCP_config.host_file = self.host_file
        self.DHCP_config.ip_address_lease_time = 1296000

    def make_client_discovery(self):
        # make a client discovery
        test_client_discovery = dhcp.dhcp.WriteBootProtocolPacket(self.DHCP_config)
        test_client_discovery.message_type = 1  # 1 for client -> server
        test_client_discovery.dhcp_message_type = 'DHCPDISCOVER'
        test_client_discovery.client_mac_address = self.client_mac
        self.transaction_id = randint(0, 1000)
        test_client_discovery.transaction_id = self.transaction_id
        test_client_discovery.parameter_request_list = []
        return test_client_discovery

    def make_client_request(self):
        # make a client request
        # client need to get the ip from server's packets
        test_client_request = dhcp.dhcp.WriteBootProtocolPacket(self.DHCP_config)
        test_client_request.message_type = 1  # 1 for client -> server
        test_client_request.dhcp_message_type = 'DHCPREQUEST'
        test_client_request.your_ip_address = self.server_ip  # set server ip in dhcp offer packet
        test_client_request.requested_ip_address = self.client_ip  # assign the client ip in dhcp server
        test_client_request.transaction_id = self.transaction_id
        test_client_request.parameter_request_list = []
        return test_client_request

    def test_DHCPSever(self):
        # set up client host
        self.create_test_host()
        self.create_HostDatabase()
        self.create_DHCPServerConfiguration()

        dhcp_thread = Process(target=dhcp.dhcp.do_dhcp, args=[
            self.server_ip, self.subnet_mask, self.host_file], name="dhcpd")
        dhcp_thread.start()
        time.sleep(3)

        print("start client\n")
        with socket(AF_INET, SOCK_DGRAM) as sd:
            sd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            sd.connect((self.server_ip, 67))  # DHCP port
            sd.settimeout(5)
            print("socket connected\n")
            # send discovery packet
            try:
                print('start discovery\n')
                discovery_packet = self.make_client_discovery()
                sd.send(discovery_packet.to_bytes())  # UDP port
                print('sent discovery\n')
                # should get offer from server, server broadcast
                while True:
                    server_packet = sd.recvfrom(4096)
                    server_data = ReadBootProtocolPacket(server_packet)
                    print(server_data)
                    print("get server packet")
                    if server_packet.message_type == 2 and server_packet.dhcp_message_type == 'DHCPOFFER':
                        print("get dhcp offer")
                        server_offer = server_packet
                        self.request_ip = server_offer.your_ip_address
                        offer_server_ip = server_offer.server_identifier
                        self.server_ip = offer_server_ip
                        # send request packet
                        request_packet = self.make_client_request()
                        sd.send(request_packet.to_bytes())
                    if server_packet.message_type == 2 and server_packet.dhcp_message_type == 'DHCPACK':
                        # get ack from server
                        ack_packet = server_packet
                        print("get dhcp pack [last packet]")
                        print("get client ip [ack]" + ack_packet.client_ip_address)
                        self.client_ip = ack_packet.client_ip_address
                        break
            except Exception as e:
                print(sys.exc_info())
                print(e)

            dhcp_thread.terminate()

def run_test():
    unittest.main(module=__name__, argv=sys.argv[1:])
