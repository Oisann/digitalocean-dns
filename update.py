#!/usr/bin/env python3

import os
import time
import json
import requests

api_entrypoint = 'https://api.digitalocean.com/v2'

# SETTINGS
sleep_interval = int(os.getenv('SLEEP', 300))
ttl = int(os.getenv('TTL', 300))
digitalocean_token = os.getenv('TOKEN', 'NO_TOKEN')
domain = os.getenv('DOMAIN', 'NO_DOMAIN')
subdomain = os.getenv('SUBDOMAIN', 'NO_SUBDOMAIN')

def main():
    if digitalocean_token == 'NO_TOKEN':
        print("No DigitalOcean token set!")
        exit(1)
    if domain == 'NO_DOMAIN':
        print("No domain set!")
        exit(1)
    if subdomain == 'NO_SUBDOMAIN':
        print("No subdomain set!")
        exit(1)
    
    dns_records_url = "{0}/domains/{1}/records".format(api_entrypoint, domain)
    headers = {'content-type': 'application/json', 'Authorization': 'Bearer {}'.format(digitalocean_token)}
    
    while True:
        domain_records = get_json(dns_records_url, headers)
        
        record = list(filter(lambda x: x['type'] == "A" and x['name'] == subdomain, domain_records['domain_records']))
        if len(record) == 1:
            record_id = record[0]['id']
            record_data = record[0]['data']
            json_ip = get_json('https://api.ipify.org?format=json', '')

            if 'ip' in json_ip:
                current_ip = json_ip['ip']
                update_data = {"type": "A", "name": subdomain, "data": current_ip, "ttl": ttl }
                update_url = "{}/{}".format(dns_records_url, record_id)

                if record_data != current_ip:
                    print("The existing DNS record ({}) doesn't match your current IP ({}). Updating!".format(record_data, current_ip))
                    requests.put(update_url, data=json.dumps(update_data), headers=headers)

            else:
                print("Got no IP from the API...")
        else:
            print("Found {} entries with the type A and the name {}!".format(len(record), subdomain))
        
        time.sleep(sleep_interval)

def get_json(url, header):
    r = requests.get(url, headers=header)
    return r.json()

if __name__ == "__main__":
    main()