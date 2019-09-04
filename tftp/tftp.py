# import click

from socket import AF_INET, SOCK_DGRAM, socket
from struct import unpack, pack
from threading import Thread

"""
This code is modified following Prof. Reed suggestion
"""

"""
The TFTPServer class encapsulates the methods required for running a simple TFTP server that handles only read requests
The server is initialized with a data directory, a port, as well as a connection address

The default data directory is the home directory
The default port is 69 (note: sudo must be used if using port 69)
The default connection address is that of the local machine.
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

    def __init__(self, data_dir, tftp_port, connection_address):
        self.data_dir = data_dir
        self.tftp_port = tftp_port
        self.connection_address = connection_address

    """
    Begins running the server thread
    """
    def start(self):
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        # We can specify a specific address when running the server (defaults to '')
        print("connecting to {}:{}".format(self.connection_address, self.tftp_port))
        self.server_socket.bind((self.connection_address, self.tftp_port))
        print("serving files from {} on port {}".format(self.data_dir, self.tftp_port))
        self.tftp_thread = Thread(target=self.__process_requests, name="tftpd")
        self.tftp_thread.start()

    """
    This code is responsible for handling requests (both valid and invalid) as well as ensuring data is transferred 
    properly and reliably.
    """
    def __process_requests(self):
        print("TFTP waiting for request")
        addr_dict = dict()
        # this while loop keeps our server running also accounting for ensuring the initial
        # data packet is retrieved by the host
        while True:
            pkt, addr = self.server_socket.recvfrom(self.BUFFER_SIZE)
            # the first two bytes of all TFTP packets is the opcode, so we can
            # extract that here. need network-byte order hence the '!'.
            [opcode] = unpack("!H", pkt[0:2])
            if opcode == TFTPServer.RRQ_OPCODE:
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
                addr_dict[addr] = [strings_in_RRQ[0], 0, 0]

                # data needed for our packet
                transfer_opcode = pack("!H", TFTPServer.DATA_OPCODE)

                try:
                    # opens the specified file in a read only binary form
                    transfer_file = open(
                        "{}/{}".format(self.data_dir, strings_in_RRQ[0].decode()), "rb"
                    )

                    # block_number will remain an integer for file seeking purposes
                    block_number = addr_dict[addr][1]

                    # navigate to the corresponding 512-byte window in the transfer file
                    transfer_file.seek(512 * block_number)

                    # read up to the appropriate 512 bytes of data
                    data = transfer_file.read(512)

                    if data:
                        block_number += 1
                        addr_dict[addr][1] = block_number

                        # the transfer block number is a binary string representation of the block number
                        transfer_block_number = pack("!H", block_number)

                        # construct a data packet
                        packet = transfer_opcode + transfer_block_number + data

                        # send the initial data packet
                        self.server_socket.sendto(packet, addr)
                        
                except FileNotFoundError:
                    # send an error packet to the requesting host
                    error_opcode = pack("!H", TFTPServer.ERROR_OPCODE)
                    error_code = pack("!H", 17)
                    error_message = b"No such file within the directory\0"
                    packet = error_opcode + error_code + error_message    
            elif opcode == TFTPServer.ACK_OPCODE:
                # this loop begins to execute with the intention to send the rest of the data
                # in the case that our file is of a size greater than 512 bytes
                #while True:
                # retrieve the ack information from the client
                if addr in addr_dict:
                    [acked_block] = unpack("!H", pkt[2:4])
                    if acked_block == addr_dict[addr][1]:
                        try:
                            # opens the specified file in a read only binary form
                            file_name = addr_dict[addr][0]
                            transfer_file = open(
                                "{}/{}".format(self.data_dir, file_name.decode()), "rb"
                            )

                            # block_number will remain an integer for file seeking purposes
                            block_number = addr_dict[addr][1]

                            # navigate to the corresponding 512-byte window in the transfer file
                            transfer_file.seek(512 * block_number)

                            # read up to the appropriate 512 bytes of data
                            data = transfer_file.read(512)

                            if data:
                                block_number += 1
                                addr_dict[addr][1] = block_number

                                # the transfer block number is a binary string representation of the block number
                                transfer_block_number = pack("!H", block_number)

                                # construct a data packet
                                packet = transfer_opcode + transfer_block_number + data

                                # send the initial data packet
                                self.server_socket.sendto(packet, addr)
                        except FileNotFoundError:
                            # send an error packet to the requesting host
                            error_opcode = pack("!H", TFTPServer.ERROR_OPCODE)
                            error_code = pack("!H", 17)
                            error_message = b"No such file within the directory\0"
                            packet = error_opcode + error_code + error_message

                    elif addr_dict[addr][2] < 3:
                        try:
                            # opens the specified file in a read only binary form
                            transfer_file = open(
                                "{}/{}".format(self.data_dir, addr_dict[addr][0].decode()), "rb"
                            )

                            # block_number will remain an integer for file seeking purposes
                            block_number = addr_dict[addr][1] - 1

                            # navigate to the corresponding 512-byte window in the transfer file
                            transfer_file.seek(512 * block_number)

                            # read up to the appropriate 512 bytes of data
                            data = transfer_file.read(512)

                            if data:
                                # the transfer block number is a binary string representation of the block number
                                transfer_block_number = pack("!H", block_number)

                                # construct a data packet
                                packet = transfer_opcode + transfer_block_number + data

                                # send the initial data packet
                                self.server_socket.sendto(packet, addr)
                        except FileNotFoundError:
                            # send an error packet to the requesting host
                            error_opcode = pack("!H", TFTPServer.ERROR_OPCODE)
                            error_code = pack("!H", 17)
                            error_message = b"No such file within the directory\0"
                            packet = error_opcode + error_code + error_message
                else:
                    # form an error packet and send it to the invalid TID
                    error_opcode = pack("!H", TFTPServer.ERROR_OPCODE)
                    error_code = pack("!H", 21)
                    error_message = b"incorrect TID\0"
                    packet = error_opcode + error_code + error_message
                    self.server_socket.sendto(packet, addr)
            else:
                # form an error packet and send it to the invalid TID
                error_opcode = pack("!H", TFTPServer.ERROR_OPCODE)
                error_code = pack("!H", 20)
                error_message = b"illegal operation specified\0"
                packet = error_opcode + error_code + error_message
                self.server_socket.sendto(packet, addr)

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