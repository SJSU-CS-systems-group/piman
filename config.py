import os
import re
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

#Uses dotenv package (https://github.com/theskumar/python-dotenv) to load the config variables
#from the .env file

COMMUNITY_NUMBER = os.getenv("COMMUNITY_NUMBER")
PI_NET_ADDRESS = os.getenv("PI_NET_IP_ADDRESS")
SWITCH_ADDRESS = os.getenv("SWITCH_ADDRESS")
SUBNET_MASK = os.getenv("SUBNET_MASK")
TFTP_PORT = os.getenv("TFTP_PORT")
TCP_PORT = os.getenv("TCP_PORT")
PI_ADDRESS_RANGE = []

for s in re.findall(r'\d+', str(os.getenv("PI_ADDRESS_RANGE"))):
    PI_ADDRESS_RANGE.append(int(s))

with open(os.path.abspath("./install/boot/cmdline.txt"), "a") as f:
    f.write(str(PI_NET_ADDRESS).rstrip("\n"))
