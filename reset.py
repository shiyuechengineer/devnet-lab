#!/usr/bin/env python3

import json
import time

import requests
from login import api_key, org_id
from functions import delete_tagged_networks


def main():
    # Use a single, persistent session
    session = requests.Session()

    delete_tagged_networks(api_key, org_id, 'DevNet', session)

    '''
    # API resource endpoint & headers
    url = f'https://api.meraki.com/api/v0/organizations/{org_id}/networks'
    headers = {'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'}

    # Dashboard API call to get VLANs of network
    response = session.get(url, headers=headers)
    networks = response.json()
    tagged_nets = [net for net in networks if 'tags' in net and 'DevNet' in net['tags']]
    print(f'Currently, there are {len(tagged_nets)} total networks tagged with "DevNet".')

    payload = {
        'confirmed': True,
        'synchronous': False,
        'actions': []
    }

    # Skip deleting default VLAN 1, because at least one VLAN is needed
    for n in vlans[1:min(301, len(vlans))]:
        resource = f'/networks/{net_id}/vlans/{vlan["id"]}'
        operation = 'destroy'
        body = {}

        action = {
            'resource': resource,
            'operation': operation,
            'body': body
        }
        payload['actions'].append(action)

    # Dashboard API call to delete all VLANs via action batch
    if payload['actions']:
        print(f'Attempting to delete {len(payload["actions"])} VLANs...')
        url = f'https://api.meraki.com/api/v0/organizations/{org_id}/actionBatches'
        response = session.post(url, data=json.dumps(payload), headers=headers)

        if response.ok:
            action_batch = response.json()['id']
            print(f'Successfully created action batch with ID {action_batch}! Refresh the Security & SD-WAN > Addressing & VLANs page to check on VLAN deletion process.')
        else:
            print('Encountered an error, so try again!')
    '''


if __name__ == '__main__':
    s = time.perf_counter()
    main()
    elapsed = time.perf_counter() - s
    print(f'{__file__} executed in {elapsed:0.2f} seconds.')
