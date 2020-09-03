import unittest
import socket
import sys
import math
from multiprocessing import Process
from tftp import tftp
from time import sleep
from struct import unpack, pack
import os
from subprocess import Popen, PIPE

data_dir = "./install/boot"
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
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sd, open('startTest.elf', 'wb') as file:
                sd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sd.settimeout(2)
                sleep(1)
                sd.sendto(b'\x00\x01start.elf\0', ("localhost", tftp_port))
                data, addr = sd.recvfrom(516)
                block = 0
                orig_size = os.path.getsize("install/boot/start.elf")
                block_number = math.floor(orig_size / 512)
                while data:
                    file.write(data[4:])
                    ack_opcode = pack("!H", 4)
                    ack_block = pack("!H", block)
                    block = block + 1
                    packet = ack_opcode + ack_block
                    sd.sendto(packet, addr)
                    data = sd.recv(516)
                    if block == block_number:
                        break
                file.close()
                sd.close()
                rec_size = os.path.getsize("startTest.elf")
                dif = orig_size - rec_size
                difference = abs(dif)
                os.remove("startTest.elf")
                self.assertLessEqual(difference, 5000)
        except Exception as e:
            self.fail(e)
        finally:
            tftp_thread.stop()


    def test_bootcode(self):
        tftp_port = 7070
        tftp_thread = tftp.TFTPServer(data_dir, tftp_port, ip)
        tftp_thread.start()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sd, open('bootcodeTest.bin', 'wb') as file:
                sd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sd.settimeout(2)
                sleep(1)
                sd.sendto(b'\x00\x01bootcode.bin\0', ("localhost", tftp_port))
                data, addr = sd.recvfrom(516)
                block = 0
                orig_size = os.path.getsize("install/boot/bootcode.bin")
                block_number = math.floor(orig_size / 512)
                while data:
                    file.write(data[4:])
                    ack_opcode = pack("!H", 4)
                    ack_block = pack("!H", block)
                    block = block + 1
                    packet = ack_opcode + ack_block
                    sd.sendto(packet, addr)
                    data = sd.recv(516)
                    if block == block_number:
                        break
                file.close()
                sd.close()
                rec_size = os.path.getsize("bootcodeTest.bin")
                print(f"{orig_size} {rec_size}")
                diff = orig_size - rec_size
                os.remove("bootcodeTest.bin")
                self.assertIs(diff, 0, msg=f"off by {diff} bytes")
        except Exception as e:
            self.fail(e)
        finally:
            tftp_thread.stop()


def run_test():
    unittest.main(module=__name__, argv=sys.argv[1:])

if __name__ == '__main__':
    unittest.main()
