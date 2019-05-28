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
record_type = os.getenv('RECORD', 'A')

def main():
    if digitalocean_token == 'NO_TOKEN':
        log("No DigitalOcean token set!")
        exit(1)
    if domain == 'NO_DOMAIN':
        log("No domain set!")
        exit(1)
    if subdomain == 'NO_SUBDOMAIN':
        log("No subdomain set!")
        exit(1)
    
    log("Started keeping the {0} record {1}.{2} updated with your IP.".format(record_type, subdomain, domain))

    if sleep_interval <= 0:
        update()
        exit()
    
    while True:
        update()
        time.sleep(sleep_interval)

def update():
    dns_records_url = "{0}/domains/{1}/records".format(api_entrypoint, domain)
    headers = {'content-type': 'application/json', 'Authorization': 'Bearer {}'.format(digitalocean_token)}
    domain_records = get_json(dns_records_url, headers)
    
    if 'domain_records' not in domain_records:
        log("Malformed response: {}".format(domain_records))
        exit()

    record = list(filter(lambda x: x['type'] == record_type and x['name'] == subdomain, domain_records['domain_records']))
    if len(record) == 1:
        record_id = record[0]['id']
        record_data = record[0]['data']
        json_ip = get_json('https://api.ipify.org?format=json', '')
        if 'ip' in json_ip:
            current_ip = json_ip['ip']
            update_data = {"type": record_type, "name": subdomain, "data": current_ip, "ttl": ttl }
            update_url = "{}/{}".format(dns_records_url, record_id)
            if record_data != current_ip:
                log("The existing DNS record ({0}) doesn't match your current IP ({1}). Updating!".format(record_data, current_ip))
                requests.put(update_url, data=json.dumps(update_data), headers=headers)
        else:
            log("Got no IP from the API...")
    else:
        log("Found {0} entries with the type {1} and the name {2}!".format(len(record), record_type, subdomain))

def get_json(url, header):
    r = requests.get(url, headers=header)
    return r.json()

def log(text):
    now = time.strftime("%Y-%m-%d %H:%M %Z")
    print("[{0}] {1}".format(now, text))


if __name__ == "__main__":
    main()