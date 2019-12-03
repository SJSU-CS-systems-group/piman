import os
import sys
import glob
import yaml

config = {}

file = glob.glob('*.yml')
file.extend(glob.glob('*.yaml'))
if len(file) != 1:
    print("Config file could not be found")
    sys.exit(1)

with open(file[0]) as f:
    try:
        config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(e)
