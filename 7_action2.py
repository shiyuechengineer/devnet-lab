#!/usr/bin/env python3

import json
import os.path
import sys
import time

import requests

from login import api_key, org_id
from functions import create_network, enable_vlans


count = 0


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

    # Synchronous action batches, each up to 20 actions
    payload = []
    for _ in range(5):
        payload.append(
            dict(
                {
                    'confirmed': True,
                    'synchronous': True,
                    'actions': []
                }
            )
        )

    # Loop to create payload of VLANs
    for x in range(1, 100):
        vlan = str(x).zfill(2)
        body = {
            'id': f'7{vlan}',
            'name': f'7_action2 - {vlan}',
            'subnet': f'10.7.{x}.0/24',
            'applianceIp': f'10.7.{x}.1'
        }

        resource = f'/networks/{net_id}/vlans'
        operation = 'create'
        action = {
            'resource': resource,
            'operation': operation,
            'body': body
        }
        payload[int(x/20)]['actions'].append(action)

    for p in payload:
        response = session.post(url, data=json.dumps(p), headers=headers)
        action_batch = response.json()
        if action_batch['status']['completed']:
            print(f'Successfully completed synchronous action batch with ID {action_batch["id"]}')
            count += len(action_batch['actions'])
        elif action_batch['status']['failed']:
            print(f'Failed action batch with ID {action_batch["id"]} and errors: {action_batch["status"]["errors"]}')
        else:
            print('Ran into some other error')


if __name__ == '__main__':
    s = time.perf_counter()
    main()
    elapsed = time.perf_counter() - s
    print(f'{__file__} executed in {elapsed:0.2f} seconds.')
    if count == 99:
        with open('results.csv', mode='a') as output:
            output.write(f'{__file__}, {elapsed:0.2f}\n')
