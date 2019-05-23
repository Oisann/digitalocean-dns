# digitalocean-dns
Automatically updates an A record on DigitalOcean's DNS when your IP changes.

## Usage

    docker run -d -e TOKEN='YOUR_DIGITALOCEAN_API_TOKEN' \ 
            -e DOMAIN='YOUR_DOMAIN' \
            -e SUBDOMAIN='YOUR_SUBDOMAIN' \
            -e SLEEP='UPDATE_INTERVAL_IN_SECONDS' \
            -e TTL='DNS_TTL_IN_SECONDS' \
            --restart=always \
            --name digitalocean-dns \
            oisann/digitalocean-dns:latest
