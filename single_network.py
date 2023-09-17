import subprocess
import requests
import json
import os
import threading
import base64
import time
from logger import logger
from termcolor import colored

# Collects information about local zerotier instance
os.environ['TOKEN'] = subprocess.check_output('sudo cat /var/lib/zerotier-one/authtoken.secret', shell=True, text=True).strip()
os.environ['NODEID'] = subprocess.check_output('sudo bin/zerotier-cli info | cut -d " " -f 3', shell=True, text=True).strip()

# Creates network and assigns IP rangee
headers = {
    'X-ZT1-AUTH': os.getenv('TOKEN', ''),
    'Content-Type': 'application/x-www-form-urlencoded',
}

payload = {
        "ipAssignmentPools": [{"ipRangeStart": "10.10.10.1", "ipRangeEnd": "10.10.10.254"}],
        "routes": [{"target": "10.10.10.0/24", "via": None}],
        "v4AssignMode": "zt",
        "private": True
    }

response = requests.post(
    'http://localhost:9993/controller/network/' + os.getenv('NODEID', '') + '______',
    headers=headers,
    json=payload
)

print(response, response.text)

# Joins self to network

d = json.loads(response.text)
# This is what any node joining the network needs to have
os.environ['NWID'] = d.get('id')

os.system(f'sudo zerotier-cli join {os.environ["NWID"]}')

# Authorizes self on network

headers = {
    'X-ZT1-AUTH': os.getenv('TOKEN', ''),
    'Content-Type': 'application/x-www-form-urlencoded',
}

data = '{"authorized": true}'

response = requests.post(
    'http://localhost:9993/controller/network/' + os.getenv('NWID', '') + '/member/' + os.getenv('NODEID', ''),
    headers=headers,
    data=data,
)

print(response, response.text)

time.sleep(5)

# Get info about self on new network

headers = {
    'X-ZT1-AUTH': os.getenv('TOKEN', ''),
}

response = requests.get(
    'http://localhost:9993/controller/network/' + os.getenv('NWID', '') + '/member/' + os.getenv('NODEID', ''),
    headers=headers,
)

print(response, response.text)