# import click

from socket import AF_INET, SOCK_DGRAM, socket
from struct import unpack, pack
from threading import Thread
from zipfile import ZipFile

import io
import os

"""
This code is modified following Prof. Reed suggestion
"""

"""
The TFTPServer class encapsulates the methods required for running a simple TFTP server that handles only read requests
The server is initialized with a data directory, a port, as well as a connection address

Data directory, port and connection address is specified in the configuration file
(note: sudo must be used if using port 69)
"""


class TFTPServer:
    RRQ_OPCODE = 1
    DATA_OPCODE = 3
    ACK_OPCODE = 4
    ERROR_OPCODE = 5
    # TFTP data packets consist of a 2-byte opcode, 2-byte block number, and up to 512-byte data portion
    # Although we could minimize since our server is solely getting RRQ and Ack packets we could have set
    # the buffer to a more optimized value (i.e. filenames on Mac OSX can have up to 256 characters so we
    # could limit the buffer to the max size of a RRQ packet) but for better practice it's been set to the
    # max data packet length in TFTP
    BUFFER_SIZE = 516

    # ctor for setting configurable attributes
    def __init__(self, data_dir, tftp_port, connection_address):
        self.data_dir = data_dir
        self.tftp_port = tftp_port
        self.connection_address = connection_address

    # opens install/boot in zipfile
    def res_open(self, name):
        zipfile = os.path.dirname(os.path.dirname(__file__))
        fd = None
        try:
            with ZipFile(zipfile) as z:
                fd = z.open("install/boot/" + name)
        except KeyError:
            pass  # we'll try looking in the filesystem next
        if not fd:
            fd = open("{}/{}".format(self.data_dir, name), "rb")
        if 'cmdline.txt' in name and fd:
            # we need to fixup the master address
            content = fd.read()
            fd.close()
            fd = io.BytesIO(content.replace(b'MASTER', self.connection_address.encode()))
        return fd

    """
    Begins running the server thread
    """

    def start(self):
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        # We can specify a specific address when running the server (defaults to '')
        print("connecting to {}:{}".format(
            self.connection_address, self.tftp_port))
        self.server_socket.bind((self.connection_address, self.tftp_port))
        print("serving files from {} on port {}".format(
            self.data_dir, self.tftp_port))
        self.tftp_thread = Thread(target=self.__process_requests, name="tftpd")
        self.tftp_thread.start()

    """
    This code is responsible for handling requests (both valid and invalid) as well as ensuring data is transferred
    properly and reliably.
    """

    def __process_requests(self):
        # this while loop keeps our server running also accounting for ensuring the initial
        # data packet is retrieved by the host
        # accepts RRQ's for files and starts a thread to proccess it
        print("TFTP waiting for request")
        while True:

            pkt, addr = self.server_socket.recvfrom(self.BUFFER_SIZE)

            t1 = Thread(
                target=self.__create_thread_and_process_requests, args=(pkt, addr))
            t1.daemon = True
            t1.start()
    """
    This code is responsible for handling requests. It starts a new socket with an ephemeral port
    for communication to the client. If no response is heard after 10 seconds, the socket is closed and function ends.
    """

    def __create_thread_and_process_requests(self, pkt, addr):

        # initial block number and variable for filename
        block_number = 0
        filename = ''

        # prepare the UDP socket
        client_dedicated_sock = socket(AF_INET, SOCK_DGRAM)
        # bind to 0 for an ephemeral port
        client_dedicated_sock.bind((self.connection_address, 0))
        # set timeout for the socket
        client_dedicated_sock.settimeout(10)

        # RRQ is a series of strings, the first two being the filename
        # and mode but there may also be options. see RFC 2347.
        #
        # we skip the first 2 bytes (the opcode) and split on b'\0'
        # since the strings are null terminated.
        #
        # because b'\0' is at the end of all strings split will always
        # give us an extra empty string at the end, so skip it with [:-1]
        strings_in_RRQ = pkt[2:].split(b"\0")[:-1]

        print("got {} from {}".format(strings_in_RRQ, addr))

        filename = strings_in_RRQ[0]

        # opens the file once for the socket, opening multiple times causes tftp to be slow
        try:
            transfer_file = self.res_open(strings_in_RRQ[0].decode())

            while True:

                # the first two bytes of all TFTP packets is the opcode, so we can
                # extract that here. the '!' is for big endian, and 'H' is to say it is an integer
                [opcode] = unpack("!H", pkt[0:2])

                if opcode == TFTPServer.RRQ_OPCODE:

                    # set the opcode for the packet we are sending
                    transfer_opcode = pack("!H", TFTPServer.DATA_OPCODE)

                    # read up to the appropriate 512 bytes of data
                    data = transfer_file.read(512)

                    # if data is received increment block number, contruct the packet, and send it
                    if data:
                        block_number += 1
                        transfer_block_number = pack("!H", block_number)
                        packet = transfer_opcode + transfer_block_number + data
                        client_dedicated_sock.sendto(packet, addr)

                # ACK received, so we can now read the next block, if it doesn't match resend the previous block of data
                elif opcode == TFTPServer.ACK_OPCODE:

                    [acked_block] = unpack("!H", pkt[2:4])

                    # block number matches, the block sent was successfully received
                    if acked_block == block_number:

                        data = transfer_file.read(512)

                        # if data read, increment block number, construct packet, and send it on the socket
                        if data:
                            block_number += 1
                            transfer_block_number = pack("!H", block_number)
                            packet = transfer_opcode + transfer_block_number + data
                            client_dedicated_sock.sendto(packet, addr)

                        # if no data was read, read returns b'', then EOF was reached and download complete
                        else:
                            print('download complete, closing socket')
                            client_dedicated_sock.close()
                            break

                    # if the block number doesn't match, means data sent was not received
                    # here you can just resend the data you already read because, no need for seek or another read
                    # because you already read it and it was not received, doing seek or read would slow down tftp
                    elif block_number != acked_block:

                        # decrement block number
                        block_number = block_number - 1

                        transfer_block_number = pack("!H", block_number)

                        packet = transfer_opcode + transfer_block_number + data

                        client_dedicated_sock.sendto(packet, addr)

                    else:
                        # form an error packet and send it to the invalid TID
                        error_opcode = pack("!H", TFTPServer.ERROR_OPCODE)
                        error_code = pack("!H", 21)
                        error_message = b"incorrect TID\0"
                        packet = error_opcode + error_code + error_message
                        client_dedicated_sock.sendto(packet, addr)
                else:
                    # form an error packet and send it to the invalid TID
                    error_opcode = pack("!H", TFTPServer.ERROR_OPCODE)
                    error_code = pack("!H", 20)
                    error_message = b"illegal operation specified\0"
                    packet = error_opcode + error_code + error_message
                    client_dedicated_sock.sendto(packet, addr)

                # listen for a client response for 10 seconds
                # close everything and terminate if no response
                try:
                    pkt, addr = client_dedicated_sock.recvfrom(
                        self.BUFFER_SIZE)

                except:
                    print("Socket Timed Out")
                    client_dedicated_sock.close()
                    print('closed socket')
                    break
        except FileNotFoundError:
            # send an error packet to the requesting host
            error_opcode = pack("!H", TFTPServer.ERROR_OPCODE)
            error_code = pack("!H", 17)
            error_message = b"No such file within the directory\0"
            packet = error_opcode + error_code + error_message
            client_dedicated_sock.sendto(packet, addr)
            client_dedicated_sock.close()

    def join(self):
        self.tftp_thread.join()


"""@click.command()
@click.option(
    "--data_dir",
    default=".",
    metavar="root_of_files_to_serve",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    help="the directory to use as the root of the files being served",
)
@click.option(
    "--tftp_port",
    default=69,
    metavar="UDP_listening_port",
    help="the UDP port to listen for tftp client requests",
)
@click.option(
    "--connection_address",
    default="",
    metavar="UDP_listening_address",
    help="the address to listen on for request",
)"""


def do_tftpd(data_dir, connection_address, tftp_port):
    """ this is a simple TFTP server that will listen on the specified
        port and serve data rooted at the specified data. only read
        requests are supported for security reasons.
    """
    print("Starting TFTP...")
    srvr = TFTPServer(data_dir, tftp_port, connection_address)
    srvr.start()
    srvr.join()
    print("TFTP is terminating")


if __name__ == "__main__":
    do_tftpd()
