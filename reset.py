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


if __name__ == '__main__':
    s = time.perf_counter()
    main()
    elapsed = time.perf_counter() - s
    print(f'{__file__} executed in {elapsed:0.2f} seconds.')
