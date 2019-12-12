import unittest
import subprocess
import socket
import piman
from multiprocessing import Process
from subprocess import PIPE, Popen


class piman_tests(unittest.TestCase):
    
    def test_makezipapp(self):
        try:
            out = subprocess.check_output(['./make_zipapp.sh'])
        except ModuleNotFoundError as e:
            self.fail("Module not Found")
        except subprocess.CalledProcessError as e:
            self.fail("Errors occured")
        except Exception as e:
            self.fail("Unexcpected exception")
        print("make_zipapp.sh ran successfully\ntesting pyz file...")
        try:
            piman = Popen(['python3', 'build/piman.pyz', 'restart' , '127.0.0.1', '30'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            print("Doing an SNPM walk to turn off and on a non-existing pi. Please wait a few seconds")
            temp = piman.communicate()
        except Exception as e:
            print(e)
        self.assertIn("Setting pi at port", str(temp), "piman.pyz method restart did not run successfully")


if __name__ == '__main__':
    unittest.main()