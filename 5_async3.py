#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor
import json
import os.path
import sys
import time

import asyncio
import requests

from login import api_key, org_id
from functions import create_network, enable_vlans


count = 0


def post(session, url, headers, payload):
    global count

    while True:
        response = session.post(url, headers=headers, data=json.dumps(payload))
        if response.ok:
            vlan = payload['id']
            print(f'Created VLAN {vlan}')
            count += 1
            break
        else:
            print(f'{response.status_code} - {response.text}')
            time.sleep(0.5)

    return response


async def main():
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
    count = 0
    payloads_to_post = []
    for x in range(1, 100):
        vlan = str(x).zfill(2)
        payload = {
            'id': f'1{vlan}',
            'name': f'{name} - {vlan}',
            'subnet': f'10.0.{x}.0/24',
            'applianceIp': f'10.0.{x}.1'
        }
        payloads_to_post.append(payload)

    # Use asynchronous calls with one thread
    with ThreadPoolExecutor(max_workers=3) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                executor,
                post,
                *(session, url, headers, payload)  # Allows us to pass in multiple arguments to `post`
            )
            for payload in payloads_to_post
        ]
        for response in await asyncio.gather(*tasks):
            pass


if __name__ == '__main__':
    s = time.perf_counter()
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(main())
    loop.run_until_complete(future)
    elapsed = time.perf_counter() - s
    print(f'{__file__} executed in {elapsed:0.2f} seconds.')
    if count == 99:
        with open('results.csv', mode='a') as output:
            output.write(f'{__file__}, {elapsed:0.2f}\n')
