import socket
import threading
from piman import logger
import logging

import serializeme as serialize


class DNSServer:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 53
        self.network_addr, self.dns_domain, self.dns_servers = self.read_piman_yml()

    def read_piman_yml(self):
        domain, servers = '', []
        with open('./piman.yaml') as rf:
            for line in rf.readlines():
                if 'dns_domain' in line:
                    domain = line.split(':')[-1].strip()
                elif 'dns_servers' in line:
                    for server in line.split(':')[-1].split(','):
                        servers.append(server.strip())
                elif 'switch_address' in line:
                    network_addr = '.'.join(line.split(':')[-1].strip().split('.')[:-1])
            return network_addr, domain, servers

    def start(self):
        while True:
            dns_thread = threading.Thread(target=self.process_requests, args=())
            dns_thread.start()
            dns_thread.join()

    def process_requests(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.host, self.port))
        res = self.server_socket.recvfrom(1024)
        data, from_client = res[0], res[1]

        pack = serialize.Deserialize(data, {
            'ID': '2B',
            'Flags': '2B',
            'Questions': '2B',
            'Answer RRs': '2B',
            'Authority RRs': '2B',
            'Additional RRs': '2B',
            'Name': (serialize.PREFIX_LEN_NULL_TERM, serialize.HOST),
            'Type': '2B',
            'class': '2B',
            'addtionals': '11B'
        })

        dns_name = pack.get_field('Name').value
        dns_type = pack.get_field('Type').value

        if dns_name == 'metrics.{}'.format(self.dns_domain) and dns_type == 33:
            self.resolve_srv_records(from_client, pack)
        elif '.'.join(dns_name.split('.')[1:]) == self.dns_domain and dns_type == 1:
            self.resolve_host(from_client, pack)
        elif dns_type == 12:
            ip = '.'.join(dns_name.replace('.in-addr.arpa', '').split('.')[::-1])
            if self._is_pi_ip(ip):
                self.resolve_ip(from_client, pack)
            else:
                self.relay_dns(data, from_client)
        else:
            self.relay_dns(data, from_client)

    def _is_pi_ip(self, ip):
        with open('./hosts.csv') as rf:
            return ip in ''.join(rf.readlines())

    def _get_host_bytes(self, host):
            data = bytearray()
            for part in host.split('.'):
                data += bytearray([len(part)])
                data += str.encode(part)
            return data + bytearray(b'\x00')

    def _get_all_pi_ports(self):
        with open('./hosts.csv') as rf:
            lines = rf.readlines()
            pi_ports = [line.split(';')[1].split('.')[-1] for line in lines]
            return pi_ports

    def _get_query_section(self, pack):
        q_name = pack.get_field('Name').value
        q_type = pack.get_field('Type').value
        q_class = pack.get_field('class').value

        data = bytearray()
        for part in q_name.split('.'):
            data += bytearray([len(part)])
            data += str.encode(part)
        data += b'\x00'

        rest = serialize.Serialize({
            'Type': ('2B', int(q_type)),
            'class': ('2B', int(q_class))
        }).packetize()

        data += rest

        return data

    def resolve_srv_records(self, from_client, pack):

        def get_anwsers():
            answers = bytearray()
            pi_ports = self._get_all_pi_ports()
            for port in pi_ports:
                domain = 'pi{}.{}'.format(port, self.dns_domain)

                answer = bytearray(b'\xc0\x0c')
                answer += serialize.Serialize({
                    'Type': ('2B', 33),
                    'class': ('2B', 1),
                    'TTL': ('4B', 300)
                }).packetize()

                target = self._get_host_bytes(domain)
                data_length = 2 + 2 + 2 + len(target)
                answer += serialize.Serialize({
                    'Data length': ('2B', data_length),
                    'Priority': ('2B', 1),
                    'Weight': ('2B', 1),
                    'Port': ('2B', 9100)
                }).packetize()
                answer += target
                answers += answer

            return answers, len(pi_ports)

        self.server_socket.connect(from_client)
        query = self._get_query_section(pack)
        answers, num_answers = get_anwsers()
        header = serialize.Serialize({
            'ID': ('2B', pack.get_field('ID').value),
            'Response': (1, 1),
            'Opcode': 4,
            'Authoritative': 1,
            'Truncated': 1,
            'RD': (1, 1),
            'RA': (1, 1),
            'Z': 1,
            'Answer authenticated': 1,
            'non-auth data': 1,
            'Reply code': 4,
            'Questions': ('2B', 1),
            'Answer RRs': ('2B', num_answers),
            'Authority RRs': '2B',
            'Additional RRs': '2B'
        }).packetize()
        res = header + query + answers
        self.server_socket.send(res)

    def resolve_ip(self, from_client, pack):
        self.server_socket.connect(from_client)

        header = serialize.Serialize({
            'ID': ('2B', pack.get_field('ID').value),
            'Response': (1, 1),
            'Opcode': 4,
            'Authoritative': 1,
            'Truncated': 1,
            'RD': (1, 1),
            'RA': (1, 1),
            'Z': 1,
            'Answer authenticated': 1,
            'non-auth data': 1,
            'Reply code': 4,
            'Questions': ('2B', 1),
            'Answer RRs': ('2B', 1),
            'Authority RRs': '2B',
            'Additional RRs': ('2B', 1)
        }).packetize()

        query = self._get_query_section(pack)

        # prepare anwser section
        pi_port = pack.get_field('Name').value.split('.')[0]
        host = 'pi{}.{}'.format(pi_port, self.dns_domain)
        domain_name = self._get_host_bytes(host)
        data_length = len(domain_name)

        answer = bytearray(b'\xc0\x0c')
        answer += serialize.Serialize({
            'Type': ('2B', 12),
            'class': ('2B', 1),
            'TTL': ('4B', 4150),
            'Data length': ('2B', data_length)
        }).packetize()
        answer += domain_name
        res = header + query + answer

        self.server_socket.send(res)

    def resolve_host(self, from_client, pack):

        def _get_mapped_ip(host):
            pi_port = host.split('.')[0].replace('pi', '')
            ip = '{}.{}'.format(self.network_addr, pi_port)

            if self._is_pi_ip(ip):
                return ip
            else:
                raise Exception('Invalid IP')

        self.server_socket.connect(from_client)

        header = serialize.Serialize({
            'ID': ('2B', pack.get_field('ID').value),
            'Response': (1, 1),
            'Opcode': 4,
            'Authoritative': 1,
            'Truncated': 1,
            'RD': (1, 1),
            'RA': (1, 1),
            'Z': 1,
            'Answer authenticated': 1,
            'non-auth data': 1,
            'Reply code': 4,
            'Questions': ('2B', 1),
            'Answer RRs': ('2B', 1),
            'Authority RRs': '2B',
            'Additional RRs': '2B'
        }).packetize()

        query = self._get_query_section(pack)

        # prepare anwser section
        ip = _get_mapped_ip(pack.get_field('Name').value)
        ip_bytes = bytes(map(int, ip.split('.')))
        data_length = len(ip_bytes)

        answer = bytearray(b'\xc0\x0c')
        answer += serialize.Serialize({
            'Type': ('2B', 1),
            'class': ('2B', 1),
            'TTL': ('4B', 24),
            'Data length': ('2B', data_length)
        }).packetize()
        answer += ip_bytes

        res = header + query + answer

        self.server_socket.send(res)

    def relay_dns(self, req, from_client):
        resolver_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        resolver_sock.connect((self.dns_servers[0], 53))
        resolver_sock.send(req)
        res = resolver_sock.recv(1024)

        self.server_socket.connect(from_client)
        self.server_socket.send(res)


def do_dns():
    logger.info("DNS server is running...")
    server = DNSServer()
    server.start()


if __name__ == '__main__':
    do_dns()
