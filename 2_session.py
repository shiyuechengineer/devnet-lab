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
    url = f'https://api.meraki.com/api/v0/networks/{net_id}/vlans'
    headers = {'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'}

    # Loop to create VLANs
    for x in range(1, 100):
        vlan = str(x).zfill(2)
        payload = {
            'id': f'1{vlan}',
            'name': f'{name} - {vlan}',
            'subnet': f'10.0.{x}.0/24',
            'applianceIp': f'10.0.{x}.1'
        }

        # Dashboard API call
        response = session.post(url, headers=headers, data=json.dumps(payload))
        if response.ok:
            print(f'Created VLAN 1{vlan}')
            count += 1
        else:
            print(f'{response.status_code} - {response.text}')


if __name__ == '__main__':
    s = time.perf_counter()
    main()
    elapsed = time.perf_counter() - s
    print(f'{__file__} executed in {elapsed:0.2f} seconds.')
    if count == 99:
        with open('results.csv', mode='a') as output:
            output.write(f'{__file__}, {elapsed:0.2f}\n')
