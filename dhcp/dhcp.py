#!/usr/bin/python3
import time
import threading
import queue
import collections
import traceback
import socket
from random import randrange
import uuid
from .listener import *
from piman import logger
import csv


"""
This class contains specified attributes which will be populated, these attributes are associated with
the required options for our DHCP+PXE server. 
"""

class WriteBootProtocolPacket(object):

    message_type = 2  # 1 for client -> server 2 for server -> client
    hardware_type = 1
    hardware_address_length = 6
    hops = 0

    transaction_id = None

    seconds_elapsed = 0
    bootp_flags = 0  # unicast

    # The following are set, but altered within the "send_offer" function inside the transaction class
    client_ip_address = '0.0.0.0'
    your_ip_address = '0.0.0.0'
    next_server_ip_address = '0.0.0.0'
    relay_agent_ip_address = '0.0.0.0'
    
    vendor_class_identifier = "PXEClient"
    boot_file_name = "bootcode.bin"
    client_mac_address = None
    magic_cookie = '99.130.83.99'

    parameter_order = []
    
    # Adds new attributes to the WriteBootProtocolPacket object for
    # each option that is present in the DHCP server configuration.
    # These attributes are used when constructing the BOOTP packet.
    def __init__(self, configuration):
        for i in range(256):
            option_name = 'option_{}'.format(i)
            if i < len(options) and hasattr(configuration, options[i][0]):
                option_name = options[i][0]
            if hasattr(configuration, option_name):
                setattr(self, option_name, getattr(configuration, option_name))

    def to_bytes(self):
        result = bytearray(236)
        
        result[0] = self.message_type
        result[1] = self.hardware_type
        result[2] = self.hardware_address_length
        result[3] = self.hops

        result[4:8] = struct.pack('>I', self.transaction_id)

        result[8:10] = shortpack(self.seconds_elapsed)
        result[10:12] = shortpack(self.bootp_flags)

        result[12:16] = inet_aton(self.client_ip_address)
        result[16:20] = inet_aton(self.your_ip_address)
        result[20:24] = inet_aton(self.next_server_ip_address)
        result[24:28] = inet_aton(self.relay_agent_ip_address)

        result[28:28 + self.hardware_address_length] = macpack(self.client_mac_address)
        
        result += inet_aton(self.magic_cookie)

        for option in self.options:
            value = self.get_option(option)
            # print(option, value)
            if value is None:
                continue
            result += bytes([option, len(value)]) + value
        result += bytes([255])
        return bytes(result)

    def get_option(self, option):
        if option < len(options) and hasattr(self, options[option][0]):
            value = getattr(self, options[option][0])
        elif hasattr(self, 'option_{}'.format(option)):
            value = getattr(self, 'option_{}'.format(option))
        else:
            return None
        function = options[option][2]
        if function and value is not None:
            value = function(value)
        return value
    
    @property
    def options(self):
        done = list()
        # fulfill wishes
        if self.parameter_order:
            for option in self.parameter_order:
                if option < len(options) and hasattr(self, options[option][0]) or hasattr(self, 'option_{}'.format(option)):
                    # this may break with the specification because we must try to fulfill the wishes
                    if option not in done:
                        done.append(option)
        # add my stuff
        for option, o in enumerate(options):
            if o[0] and hasattr(self, o[0]):
                if option not in done:
                    done.append(option)
        for option in range(256):
            if hasattr(self, 'option_{}'.format(option)):
                if option not in done:
                    done.append(option)
        return done

    def __str__(self):
        return str(ReadBootProtocolPacket(self.to_bytes()))

class DelayWorker(object):

    def __init__(self):
        self.closed = False
        self.queue = queue.PriorityQueue()
        self.thread = threading.Thread(target=self._delay_response_thread)
        self.thread.start()

    def _delay_response_thread(self):
        while not self.closed:
            p = self.queue.get()
            if self.closed:
                break
            t, func, args, kw = p
            now = time.time()
            if now < t:
                time.sleep(0.01)
                self.queue.put(p)
            else:
                func(*args, **kw)

    def do_after(self, seconds, func, args=(), kw={}):
        self.queue.put((time.time() + seconds, func, args, kw))

    def close(self):
        self.closed = True

"""
The transaction class handles data transfers. One of the key functions here is the "send_offer" function which is 
responsible for sending out the initial offer packet. It is also responsible for receiving the initial DHCP Discover 
packet which is broadcast by the client.
"""
class Transaction(object):

    def __init__(self, server):
        self.server = server
        self.configuration = server.configuration
        self.packets = []
        self.done_time = time.time() + self.configuration.length_of_transaction
        self.done = False
        self.do_after = self.server.delay_worker.do_after

    def is_done(self):
        return self.done or self.done_time < time.time()

    def close(self):
        self.done = True

    def receive(self, packet):
        # packet from client <-> packet.message_type == 1
        if packet.message_type == 1 and packet.dhcp_message_type == 'DHCPDISCOVER':
            self.do_after(self.configuration.dhcp_offer_after_seconds,
                          self.received_dhcp_discover, (packet,), )
        elif packet.message_type == 1 and packet.dhcp_message_type == 'DHCPREQUEST':
            self.do_after(self.configuration.dhcp_acknowledge_after_seconds,
                          self.received_dhcp_request, (packet,), )
        elif packet.message_type == 1 and packet.dhcp_message_type == 'DHCPINFORM':
            self.received_dhcp_inform(packet)
        else:
            return False
        return True

    def received_dhcp_discover(self, discovery):
        if self.is_done(): return
        self.configuration.debug('discover:\n {}'.format(str(discovery).replace('\n', '\n\t')))
        should_send_offer = False
        for known_host in self.server.hosts.get():
            if discovery.client_mac_address == known_host.to_tuple()[0]:
                should_send_offer = True
    
        if should_send_offer:
            self.send_offer(discovery)
        else:
            unknown_mac_addr = discovery.client_mac_address
            logger.error("unknown mac_address {}. will not assign ip.".format(unknown_mac_addr))
            self.mac_mapper(unknown_mac_addr)

    def mac_mapper(self, unknown_mac):
        with open('addr_database.csv', 'r') as f:
            reader - csv.reader(f, delimiter=',')
            for row in reader:
                if unknown_mac.startswith(row[0]):
                    logger.debug('{} is from the Company: {}'.format(unknown_mac, row[1]))

    def send_offer(self, discovery):
        # https://tools.ietf.org/html/rfc2131
        offer = WriteBootProtocolPacket(self.configuration)
        offer.parameter_order = discovery.parameter_request_list
        mac = discovery.client_mac_address
        ip = offer.your_ip_address = self.server.get_ip_address(discovery)
        offer.transaction_id = discovery.transaction_id
        offer.relay_agent_ip_address = discovery.relay_agent_ip_address
        offer.client_mac_address = mac
        offer.client_ip_address = discovery.client_ip_address or '0.0.0.0'
        offer.bootp_flags = discovery.bootp_flags
        offer.dhcp_message_type = 'DHCPOFFER'
        offer.server_identifier = self.server.configuration.ip
        offer.client_identifier = mac
        offer.ip_address_lease_time = self.configuration.ip_address_lease_time
        pkt = construct_packet(mac, self.configuration.ip, ip, offer)
        self.server.unicast(pkt)
    
    def received_dhcp_request(self, request):
        if self.is_done(): return
        self.server.client_has_chosen(request)
        self.acknowledge(request)
        self.close()

    def acknowledge(self, request):
        ack = WriteBootProtocolPacket(self.configuration)
        ack.parameter_order = request.parameter_request_list
        ack.transaction_id = request.transaction_id
        ack.bootp_flags = request.bootp_flags
        ack.relay_agent_ip_address = request.relay_agent_ip_address
        mac = request.client_mac_address
        ack.client_mac_address = mac
        requested_ip_address = request.requested_ip_address
        ack.client_ip_address = request.client_ip_address or '0.0.0.0'
        ack.your_ip_address = self.server.get_ip_address(request)
        ack.dhcp_message_type = 'DHCPACK'
        ack.server_identifier = self.server.configuration.ip
        ack.ip_address_lease_time = self.configuration.ip_address_lease_time
        pkt = construct_packet(mac, self.server.configuration.ip,
                request.requested_ip_address or request.client_ip_address, ack)
        self.server.unicast(pkt)

    def received_dhcp_inform(self, inform):
        self.close()
        self.server.client_has_chosen(inform)

class DHCPServerConfiguration(object):
    
    dhcp_offer_after_seconds = 1  # must be >0!!!
    dhcp_acknowledge_after_seconds = 10
    length_of_transaction = 40

    #network = '192.168.173.0'
    #broadcast_address = '255.255.255.255'
    #subnet_mask = '255.255.255.0'
    #router = '172.30.3.1'
    domain_name_server = None # list of ips

    debug = lambda *args, **kw: None

    def __init__(self, ip, subnet_mask, hosts_file, lease_time, net_inter):
        self.ip = ip
        self.subnet_mask = subnet_mask
        self.host_file = hosts_file
        self.ip_address_lease_time = lease_time
        self.net_inter_name = net_inter
        self.network = network_from_ip_subnet(ip, subnet_mask)
        self.router = ip
        self.domain_name_server = ['8.8.8.8'] # list of IPs
        self.network_time_protocol_servers = [ip]

    def load(self, file):
        with open(file) as f:
            exec(f.read(), self.__dict__)


    def all_ip_addresses(self):
        ips = ip_addresses(self.network, self.subnet_mask)
        for i in range(5):
            next(ips)
        return ips

    def network_filter(self):
        return NETWORK(self.network, self.subnet_mask)

class ALL(object):
    def __eq__(self, other):
        return True
    def __repr__(self):
        return self.__class__.__name__
ALL = ALL()


class NETWORK(object):
    def __init__(self, network, subnet_mask):
        self.subnet_mask = struct.unpack('>I', inet_aton(subnet_mask))[0]
        self.network = struct.unpack('>I', inet_aton(network))[0]
    def __eq__(self, other):
        ip = struct.unpack('>I', inet_aton(other))[0]
        return ip & self.subnet_mask == self.network and \
               ip - self.network and \
               ip - self.network != ~self.subnet_mask & 0xffffffff
        
class CASEINSENSITIVE(object):
    def __init__(self, s):
        self.s = s.lower()
    def __eq__(self, other):
        return self.s == other.lower()

class CSVDatabase(object):

    delimiter = ';'

    def __init__(self, file_name):
        self.file_name = file_name
        self.file('a').close()  # create file

    def file(self, mode='r'):
        return open(self.file_name, mode)

    def get(self, pattern):
        pattern = list(pattern)
        return [line for line in self.all() if pattern == line]

    def add(self, line):
        with self.file('a') as f:
            f.write(self.delimiter.join(line) + '\n')

    def delete(self, pattern):
        lines = self.all()
        lines_to_delete = self.get(pattern)
        self.file('w').close()  # empty file
        for line in lines:
            if line not in lines_to_delete:
                self.add(line)

    def all(self):
        with self.file() as f:
            return [list(line.strip().split(self.delimiter)) for line in f]

class Host(object):

    def __init__(self, mac, ip, hostname, last_used):
        self.mac = mac.upper()
        self.ip = ip
        self.hostname = hostname
        self.last_used = int(last_used)

    @classmethod
    def from_tuple(cls, line):
        mac, ip, hostname, last_used = line
        last_used = int(last_used)
        return cls(mac, ip, hostname, last_used)

    @classmethod
    def from_packet(cls, packet):
        return cls(packet.client_mac_address,
                   packet.requested_ip_address or packet.client_ip_address,
                   packet.host_name or '',
                   int(time.time()))

    @staticmethod
    def get_pattern(mac=ALL, ip=ALL, hostname=ALL, last_used=ALL):
        return [mac, ip, hostname, last_used]

    def to_tuple(self):
        return [self.mac, self.ip, self.hostname, str(int(self.last_used))]

    def to_pattern(self):
        return self.get_pattern(ip=self.ip, mac=self.mac)

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other):
        return self.to_tuple() == other.to_tuple()

    def has_valid_ip(self):
        return self.ip and self.ip != '0.0.0.0'
        

class HostDatabase(object):
    def __init__(self, file_name):
        self.db = CSVDatabase(file_name)

    def get(self, **kw):
        pattern = Host.get_pattern(**kw)
        return list(map(Host.from_tuple, self.db.get(pattern)))

    def add(self, host):
        if(self.eval(host)):
            self.db.add(host.to_tuple())
        else:
            print("invalid host {}, cannot add".format(host.to_tuple()))

    def delete(self, host=None, **kw):
        if host is None:
            pattern = Host.get_pattern(**kw)
        else:
            pattern = host.to_pattern()
        self.db.delete(pattern)

    def all(self):
        return list(map(Host.from_tuple, self.db.all()))

    def replace(self, host):
        self.delete(host)
        self.add(host)

    def eval(self,host):
        result = True
        for element in self.all():
            if(host.mac == element.mac):
                if(host.ip != element.ip):    
                    result = False
            if(host.mac[0]=="5"):
                result = False
        return result
        
class DHCPServer(object):

    def __init__(self, configuration=None):
        if configuration == None:
            configuration = DHCPServerConfiguration()
        self.configuration = configuration
        self.socket = socket(type = SOCK_DGRAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.bind(('', 67))  # Using '' instead to broadcast to all
        self.delay_worker = DelayWorker()
        self.closed = False
        self.transactions = collections.defaultdict(lambda: Transaction(self))  # id: transaction
        self.hosts = HostDatabase(self.configuration.host_file)
        self.raw_sock = socket(AF_PACKET, SOCK_RAW)
        self.raw_sock.bind((self.configuration.net_inter_name, 0)) # ETH_P_ALL = 0
        self.time_started = time.time()

    def close(self):
        self.socket.close()
        self.closed = True
        self.delay_worker.close()
        for transaction in list(self.transactions.values()):
            transaction.close()

    def update(self, timeout=0):
        try:
            reads = select.select([self.socket], [], [], timeout)[0]
        except ValueError:
            # ValueError: file descriptor cannot be a negative integer (-1)
            logger.error("Value error: file descriptor cannot be a negative integer")
            return
        for socket in reads:
            try:
                packet = ReadBootProtocolPacket(*socket.recvfrom(4096))
                # print(packet)
            except OSError:
                # OSError: [WinError 10038] An operation was attempted on something that is not a socket
                logger.error("OSError - operation was attempted on something that is not a socket")
                pass
            else:
                self.received(packet)
        for transaction_id, transaction in list(self.transactions.items()):
            if transaction.is_done():
                transaction.close()
                self.transactions.pop(transaction_id)

    def received(self, packet):
        if not self.transactions[packet.transaction_id].receive(packet):
            self.configuration.debug('received:\n {}'.format(str(packet).replace('\n', '\n\t')))
            
    def client_has_chosen(self, packet):
        self.configuration.debug('client_has_chosen:\n {}'.format(str(packet).replace('\n', '\n\t')))
        host = Host.from_packet(packet)
        if not host.has_valid_ip():
            return
        self.hosts.replace(host)

    def is_valid_client_address(self, address):
        if address is None:
            return False
        # print(address)
        # print(self.configuration.subnet_mask)
        # print(self.configuration.network)
        a = address.split('.')
        s = self.configuration.subnet_mask.split('.')
        n = self.configuration.network.split('.')
        return all(s[i] == '0' or a[i] == n[i] for i in range(4))

    def get_ip_address(self, packet):
        mac_address = packet.client_mac_address
        requested_ip_address = packet.requested_ip_address
        known_hosts = self.hosts.get(mac = CASEINSENSITIVE(mac_address))
        ip = None
        if known_hosts:
            # 1. choose known ip address
            for host in known_hosts:
                if self.is_valid_client_address(host.ip):
                    ip = host.ip
            str_known_ip = "known ip: " + str(ip)
            logger.info(str_known_ip)
        if ip is None and self.is_valid_client_address(requested_ip_address):
            # 2. choose valid requested ip address
            ip = requested_ip_address
            str_valid_ip = "valid ip: " + str(ip)
            logger.info(str_valid_ip)
        if ip is None:
            # 3. choose new, free ip address
            chosen = False
            network_hosts = self.hosts.get(ip=self.configuration.network_filter())
            for ip in self.configuration.all_ip_addresses():
                if not any(host.ip == ip for host in network_hosts):
                    chosen = True
                    break
            if not chosen:
                # 4. reuse old valid ip address
                network_hosts.sort(key=lambda host: host.last_used)
                ip = network_hosts[0].ip
                assert self.is_valid_client_address(ip)
            str_new_ip = "new ip: " + str(ip)
            logger.info(str_new_ip)
        if not any([host.ip == ip for host in known_hosts]):
            str_add_mac = "add " + str(mac_address) + "ip: " + str(ip) + "hostname: " + str(packet.host_name)
            logger.info(str_add_mac)
            #print('add', mac_address, ip, packet.host_name)
            self.hosts.replace(Host(mac_address, ip, packet.host_name or '', time.time()))
        return ip

    @property
    def server_identifiers(self):
        return [self.configuration.ip]

    def broadcast(self, packet):
        self.configuration.debug('broadcasting:\n {}'.format(str(packet).replace('\n', '\n\t')))
        try:
            data = packet.to_bytes()
            self.broadcast_socket.sendto(data, ('255.255.255.255', 68))
        except:
            logger.error('error broadcasting')
            traceback.print_exc()

    def unicast(self, packet):
        try:
            self.raw_sock.send(packet)
        except:
            logger.error('DCHP - error unicasting')
            traceback.print_exc()

    def run(self):
        while not self.closed:
            try:
                self.update(1)
            except KeyboardInterrupt:
                logger.exception("keyboard interrupt")
                break
            except:
                logger.error(traceback.print_exc())
                traceback.print_exc()

# Produces a list of inet addresses associated with the local host.
def get_host_ip_addresses():
    return gethostbyname_ex(gethostname())[2]

# Produces the subnet address from an inet address and a subnet mask.
def network_from_ip_subnet(ip, subnet_mask):
    import socket
    subnet_mask = struct.unpack('>I', socket.inet_aton(subnet_mask))[0]
    ip = struct.unpack('>I', socket.inet_aton(ip))[0]
    network = ip & subnet_mask
    return socket.inet_ntoa(struct.pack('>I', network))

# Produces an iterator containing all the host inet addresses on a subnet.
def ip_addresses(network, subnet_mask):
    import socket, struct
    subnet_mask = struct.unpack('>I', socket.inet_aton(subnet_mask))[0]
    network = struct.unpack('>I', socket.inet_aton(network))[0]
    network = network & subnet_mask
    start = network + 1
    end = (network | (~subnet_mask & 0xffffffff)) # ???
    return (socket.inet_ntoa(struct.pack('>I', i)) for i in range(start, end))

def sorted_hosts(hosts):
    hosts = list(hosts)
    hosts.sort(key = lambda host: (host.hostname.lower(), host.mac.lower(), host.ip.lower()))
    return hosts

# 'Empty' packet data. Filled in when DHCP sends unicast responses.
UDP   = b'\x00\x43\x00\x44\x00\x00\x00\x00'
IP    = b'\x45\x00\x00\x00\x00\x00\x40\x00\x40\x11\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
ETHER = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00'

def construct_packet(dmac, sip, dip, bootp):
    # BOOTP Payload
    bootp = bootp.to_bytes()
    udp   = bytearray(UDP)
    ip    = bytearray(IP)
    ether = bytearray(ETHER)

    # UDP Packet
    udp_length = len(bootp) + 8
    udp[4:6] = (udp_length).to_bytes(2, 'big')
    #udp[6:7] = UDP checksum

    # IP Packet
    ip[ 2: 4] = (udp_length + 20).to_bytes(2, 'big')
    ip[ 4: 6] = (randrange(0, 65535)).to_bytes(2, 'big')
    ip[12:16] = inet_aton(sip)
    ip[16:20] = inet_aton(dip)
    ip[10:12] = IP_checksum(ip)

    # Ethernet Frame
    ether[0: 6] = macpack(dmac)
    ether[6:12] = (uuid.getnode()).to_bytes(6, 'big')

    packet = b''.join([bytes(ether), bytes(ip), bytes(udp), bootp])
    return packet

# https://github.com/mdelatorre/checksum/blob/master/ichecksum.py
def IP_checksum(data):
    sum = 0
    for i in range(0,len(data),2):
        if i + 1 >= len(data):
            sum += data[i] & 0xFF
        else:
            w = ((data[i] << 8) & 0xFF00) + (data[i+1] & 0xFF)
            sum += w

    while (sum >> 16) > 0:
        sum = (sum & 0xFFFF) + (sum >> 16)

    sum = ~sum
    sum = sum & 0xFFFF

    return (sum).to_bytes(2, 'big') 

def do_dhcp(hosts_file, subnet_mask, ip, lease_time, net_inter):
    configuration = DHCPServerConfiguration(ip, subnet_mask, hosts_file,
            lease_time, net_inter)
    configuration.tftp_server_name = ip
    #configuration.debug = print
    #configuration.adjust_if_this_computer_is_a_router()
    #configuration.router #+= ['192.168.0.1']
    server = DHCPServer(configuration)
    for ip in server.configuration.all_ip_addresses():
        assert ip == server.configuration.network_filter()
    logger.info("DHCP server is running...")
    server.run()
    
    
if __name__ == '__main__':
    do_dhcp()
