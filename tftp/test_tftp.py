import unittest
import socket
import sys
import math
from multiprocessing import Process
from tftp import tftp
from time import sleep
from struct import unpack, pack
import struct
import os
from subprocess import Popen, PIPE

data_dir = "./firmware/boot"
ip = '127.0.0.1'

class tftp_tests(unittest.TestCase):
    '''
    
    Note: BECAUSE TFTP.PY DOES NOT TERMINATE, YOU WILL HAVE TO CTRL-C TWICE TO EXIT AFTER THE TESTS END (The threads are running still).
    To run the test cases with the piman TFTP, you will have to first run ./make_zipapp.sh to make the piman.pyz file, and then run
    sudo python3 build/piman.pyz run-tftp-test. 
    This needs to be done through piman.pyz because in TFTP, we open a zipfile that is the current directory, and this only works within piman.pyz.
    
    test_start will test transferring the start.elf file. The reason we have a break statement is because
    of how tftp thread works. the tftp thread will always be running (while True:), so in order to continue on,
    we have to break once the last block arrives.
    test_bootcode is just like test_start but we transfer bootcode.bin. This file has a different size, so we can
    test different size.
    
    If both test pass, it should say Run 2 OK with no error messages in the output. press CTRL-C twice to exit both TFTP threads now.
    '''

    def test_start(self):
        tftp_port = 6969
        tftp_thread = tftp.TFTPServer(data_dir, tftp_port, ip)
        tftp_thread.start()
        filename = "start.elf"
        try:
            with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as sd, open(f'startTest.elf',
                                                                                          'wb') as new_file:
                sd.bind(("", 0))
                opcode_request = struct.pack("!H", 1)
                opcode_data = 3
                opcode_ack = 4
                opcode_error = 5
                mode = "octet"
                # read request - opcode = 1 (for read)
                read_request = opcode_request + f"{filename}\0{mode}\0".encode()
                try:
                    sd.sendto(read_request, ("localhost", tftp_port))
                    sd.settimeout(1)
                    (data, raddr) = sd.recvfrom(516)
                    (opcode, error_code) = struct.unpack("!HH", data[0:4])  # error_code - block number
                    total_bytes = 0
                    block_numbers = set()  # to handle duplicate packets
                    orig_size = os.path.getsize(f"{data_dir}/{filename}")
                    try:
                        sd.settimeout(2)
                        while data:
                            (opcode, block_number) = struct.unpack("!HH", data[0:4])
                            if opcode == opcode_data:
                                rest = data[4:]
                                if block_number not in block_numbers:
                                    block_numbers.add(block_number)
                                    new_file.write(rest)
                                    ack = struct.pack("!HH", opcode_ack, block_number)
                                    total_bytes += len(rest)
                                    sd.sendto(ack, raddr)
                                    if len(data) < 512:
                                        print("Received", total_bytes, "bytes.")
                                        new_file.close()
                                        new_size = os.path.getsize(f"startTest.elf")
                                        sd.close()
                                        self.assertEqual(new_size, total_bytes)
                                        self.assertEqual(orig_size, total_bytes)
                                        return
                                        # exit(0)
                                    try:
                                        sd.settimeout(1)
                                        (data, raddr) = sd.recvfrom(516)
                                    except socket.timeout:
                                        (data, raddr) = sd.recvfrom(516)
                                else:
                                    # if duplicate packet received send another ack but don't write to file
                                    ack = struct.pack("!HH", opcode_ack, block_number)
                                    sd.sendto(ack, raddr)
                            else:
                                # handle random error
                                self.fail("opcodes don't match")
                    except socket.timeout:
                        new_file.close()
                        sd.close()
                        self.fail("Timed out")
                except socket.timeout:
                    print("Timeout communicating with", ("localhost", tftp_port))
                    self.fail("Timeout communicating with server")
        except Exception as e:
            self.fail(e)
        finally:
            tftp_thread.stop()


    def test_bootcode(self):
        tftp_port = 7070
        tftp_thread = tftp.TFTPServer(data_dir, tftp_port, ip)
        tftp_thread.start()
        filename = "bootcode.bin"
        try:
            with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as sd, open(f'bootcodeTest.bin',
                                                                                          'wb') as new_file:
                sd.bind(("", 0))
                opcode_request = struct.pack("!H", 1)
                opcode_data = 3
                opcode_ack = 4
                opcode_error = 5
                mode = "octet"
                # read request - opcode = 1 (for read)
                read_request = opcode_request + f"{filename}\0{mode}\0".encode()
                try:
                    sd.sendto(read_request, ("localhost", tftp_port))
                    sd.settimeout(1)
                    (data, raddr) = sd.recvfrom(516)
                    (opcode, error_code) = struct.unpack("!HH", data[0:4])  # error_code or block no
                    total_bytes = 0
                    block_numbers = set()  # to handle duplicate packets
                    orig_size = os.path.getsize(f"{data_dir}/{filename}")
                    try:
                        sd.settimeout(2)
                        while data:
                            (opcode, block_number) = struct.unpack("!HH", data[0:4])
                            if opcode == opcode_data:
                                rest = data[4:]
                                if block_number not in block_numbers:
                                    block_numbers.add(block_number)
                                    new_file.write(rest)
                                    ack = struct.pack("!HH", opcode_ack, block_number)
                                    total_bytes += len(rest)
                                    sd.sendto(ack, raddr)
                                    if len(data) < 512:
                                        print("Received", total_bytes, "bytes.")
                                        new_file.close()
                                        new_size = os.path.getsize(f"bootcodeTest.bin")
                                        sd.close()
                                        self.assertEqual(new_size, total_bytes)
                                        self.assertEqual(orig_size, total_bytes)
                                        return
                                    try:
                                        sd.settimeout(1)
                                        (data, raddr) = sd.recvfrom(516)
                                    except socket.timeout:
                                        (data, raddr) = sd.recvfrom(516)
                                else:
                                    # if duplicate packet received send another ack but don't write to file
                                    ack = struct.pack("!HH", opcode_ack, block_number)
                                    sd.sendto(ack, raddr)
                            else:
                                # handle random  error
                                self.fail("opcodes don't match")
                    except socket.timeout:
                        new_file.close()
                        sd.close()
                        self.fail("Timed out")
                except socket.timeout:
                    print("Timeout communicating with", ("localhost", tftp_port))
                    self.fail("Timeout communicating with server")
        except Exception as e:
            self.fail(e)
        finally:
            tftp_thread.stop()


def run_test():
    unittest.main(module=__name__, argv=sys.argv[1:])

if __name__ == '__main__':
    unittest.main()
