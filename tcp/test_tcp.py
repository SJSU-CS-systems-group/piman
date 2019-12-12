import unittest
import socket
import tcp
from multiprocessing import Process
from time import sleep
import os
import subprocess
import signal

'''
test_tcp.py can be run on command line by inputting the following
sudo python3 tcp/test_tcp.py

NOTE: THE TCP THREAD NEVER TERMINATES BECAUSE THE TCP THREAD IS IN A WHILE LOOP. YOU WILL HAVE TO CTRL-C TO BREAK OUT OF IT.
* Because the TCP thread never terminates, it is likely that you can only run 1 test at a time. The top test, test_tcp, is the most
important one, so that one will run first. If you want to test a specific test case, comment out the other test cases.

test_tcp tests if rootfs file is transferred when requested. If the host machine's rootfs.tgz file is the same size (or close) to 
the size of the /install/boot/rootfs file, then it passes. Else it fails.
the other 3 tests send a message to the TCP thread (IS_UNINSTALLED, IS_INSTALLED, IS_HELPFUL). The first 2 should pass,
the last one should fail.
'''

SEND_BOOT = b"boot\n" + b"EOM\n"
SEND_FORMAT = b"format\n" + b"EOM\n"

class tcp_tests(unittest.TestCase):
    

    def test_tcp(self):
        sleep(3)
        port = 3345
        tcp_thread = Process(target=tcp.do_tcp, args=["./install/boot", port, "localhost"], name="tcp")
        tcp_thread.start()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sd:
                sd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sleep(3)
                sd.connect(('localhost', port))
                sd.sendall(b'IS_FORMATTED\n')
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sd2:
                    sd2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sd2.connect(('localhost', 4444))
                    file = open('rootfs.tgz', 'wb')
                    data = sd2.recv(1024)
                    while data:
                        file.write(data)
                        data = sd2.recv(1024)
                    rec_size = os.path.getsize("rootfs.tgz")
                    orig_size =os.path.getsize("./install/boot/rootfs.tgz")
                    difference = abs(orig_size - rec_size)
                    file.close()
                    os.remove("rootfs.tgz")
                    # this was originally used instead of the assertLessEqual commented out here
                    # there seems to be a bug with tcp where the exact file is not transferred
                    # self.assertLessEqual(difference, 5000)
                    tcp_thread.terminate()
                    self.assertEqual(rec_size, orig_size)
        except KeyboardInterrupt as e:
            sd2.close()
            sd.close()
            file.close()
            os.remove("rootfs.tgz")
            tcp_thread.terminate()
        except OSError as e:
            sd2.close()
            sd.close()
            tcp_thread.terminate()
        sd2.close()
        sd.close()

    def test_installed(self):
        port = 5001
        tcp_thread = Process(target=tcp.do_tcp, args=["./install/boot", port, "localhost"], name="tcpThread1")
        tcp_thread.daemon = True
        tcp_thread.start()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sd:
                sd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sleep(2)
                sd.connect(('localhost', port))
                sd.sendall(b'IS_INSTALLED\n')
                response = sd.recv(1024)
                self.assertEqual(response, SEND_BOOT)
                sd.sendall(b'IS_UNINSTALLED\n')
                response = sd.recv(1024)
                self.assertEqual(response, SEND_FORMAT)
                sd.close()
        except KeyboardInterrupt as e:
            sd.close()
            self.fail("Cancelled before completed")
        except Exception as e:
            print(e)
            sd.close()
            self.fail("Unexpected exception")
        tcp_thread.terminate()


    # def test_uninstalled(self):
    #     sleep(13)
    #     port = 5002
    #     tcp_thread = Process(target=tcp.do_tcp, args=["./install/boot", port, "localhost"], name="tcpThread2")
    #     tcp_thread.daemon = True
    #     tcp_thread.start()
    #     try:
    #         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sd:
    #             sd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #             sleep(2)
    #             sd.connect(('localhost', port))
    #             sd.sendall(b'IS_UNINSTALLED\n')
    #             response = sd.recv(1024)
    #             self.assertEqual(response, SEND_FORMAT)
    #             sd.close()
    #     except KeyboardInterrupt as e:
    #         sd.close()
    #         self.fail("User canceled test before completion")
    #     except Exception as e:
    #         print(e)
    #         sd.close()
    #         self.fail("Unexpected exception")
    #     tcp_thread.terminate()


if __name__ == '__main__':
    unittest.main()