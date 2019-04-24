#!/usr/bin/env python3

import json
import os.path
import sys
import time

import requests

from login import api_key, org_id
from functions import create_network, enable_vlans


count = 0


# Helper function to check asynchronous action batch completion status
def check_completion(session, action_batch):
    url = f'https://api.meraki.com/api/v0/organizations/{org_id}/actionBatches/{action_batch}'
    headers = {'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'}
    response = session.get(url, headers=headers)
    if response.ok and response.json()['status']['completed']:
        num_completed = len(response.json()['actions'])
        return num_completed
    else:
        return 0


def main():
    global count

    # Use a single, persistent session
    session = requests.Session()

    # Create new network and enable VLANs
    name = os.path.basename(__file__)[:-3]
    net_id = create_network(api_key, org_id, name, session)
    if not net_id:
        sys.exit('Exiting script; please check your API key and org ID in the login.py file.')
    success = enable_vlans(api_key, net_id)
    if not success:
        sys.exit('Exiting script due to error with enabling VLANs.')

    # API resource endpoint & headers
    url = f'https://api.meraki.com/api/v0/organizations/{org_id}/actionBatches'
    headers = {'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'}

    # Asynchronous action batch
    payload = {
        'confirmed': True,
        'synchronous': False,
        'actions': []
    }

    # Loop to create payload of VLANs
    for x in range(1, 100):
        vlan = str(x).zfill(2)
        body = {
            'id': f'1{vlan}',
            'name': f'{name} - {vlan}',
            'subnet': f'10.0.{x}.0/24',
            'applianceIp': f'10.0.{x}.1'
        }

        resource = f'/networks/{net_id}/vlans'
        operation = 'create'
        action = {
            'resource': resource,
            'operation': operation,
            'body': body
        }
        payload['actions'].append(action)

    # Dashboard API call
    response = session.post(url, headers=headers, data=json.dumps(payload))
    if not response.ok:
        sys.exit(f'Exiting script due to error: {response.text}')
    action_batch = response.json()['id']
    print(f'Successfully created asynchronous action batch with ID {action_batch}')

    # Check status of API call until completed
    while True:
        num_completed = check_completion(session, action_batch)

        if num_completed > 0:
            count += num_completed
            break
        else:
            print('Still processing...')


if __name__ == '__main__':
    s = time.perf_counter()
    main()
    elapsed = time.perf_counter() - s
    print(f'{__file__} executed in {elapsed:0.2f} seconds.')
    if count == 99:
        with open('results.csv', mode='a') as output:
            output.write(f'{__file__}, {elapsed:0.2f}\n')
