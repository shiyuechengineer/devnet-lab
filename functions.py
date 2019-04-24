from datetime import datetime
import json
import time

import requests


# Helper function to create a new network
def create_network(api_key, org_id, name, session=None):
    url = f'https://mp.meraki.com/api/v0/organizations/{org_id}/networks'
    headers = {'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'}

    time_now = f'{datetime.now():%Y%m%d_%H%M%S}'
    net_name = f'{name} - {time_now}'

    payload = {
        'name': net_name,
        'type': 'appliance',
        'tags': 'DevNet',
        'timeZone': 'US/Pacific'
    }

    if session:
        response = session.post(url, headers=headers, data=json.dumps(payload))
    else:
        response = requests.post(url, headers=headers, data=json.dumps(payload))

    net_id = response.json()['id']
    if response.ok:
        print(f'Created network {net_name} with ID {net_id}')
        return net_id
    else:
        print(f'Error attempting to create network {net_name}')
        return None


# Helper function to enable VLANs
def enable_vlans(api_key, net_id, session=None):
    url = f'https://mp.meraki.com/api/v0/networks/{net_id}/vlansEnabledState'
    headers = {'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'}
    payload = {'enabled': True}

    if session:
        response = session.put(url, headers=headers, data=json.dumps(payload))
    else:
        response = requests.put(url, headers=headers, data=json.dumps(payload))

    if response.ok:
        print(f'Enabled VLANs')
        return True
    else:
        print(f'Error enabling VLANs')
        return False


# Helper function to get networks of org
def get_networks(api_key, org_id, session):
    url = f'https://api.meraki.com/api/v0/organizations/{org_id}/networks'
    headers = {'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'}

    response = session.get(url, headers=headers)
    return response.json()


# Helper function to delete a single network
def delete_network(api_key, net_id, session):
    url = f'https://api.meraki.com/api/v0/networks/{net_id}'
    headers = {'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'}

    response = session.delete(url, headers=headers)
    if response.ok:
        print(f'Deleted network {net_id}')


# Helper function to delete all networks with specified tag
def delete_tagged_networks(api_key, org_id, tag, session):
    networks = get_networks(api_key, org_id, session)
    for network in networks:
        if network['tags'] and tag in network['tags']:
            delete_network(api_key, network['id'], session)
