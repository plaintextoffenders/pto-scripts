#!/usr/bin/python
# Updates plaintextoffenders domains file based on new posts on the plaintextoffenders.com Tumblr.

import pytumblr
import re
from itertools import chain

# Domains filename. Assumes each line contains a single domain.
DOMAINS_FILENAME = '../plaintextoffenders/offenders.txt'
# Tumblr keys filename. Assumes first line is consumer key and second line is consumer secret.
KEYS_FILENAME = 'tumblr_keys'
# Limit number of posts to fetch from Tumblr.
LIMIT = 100
# Scroll size of each request from Tumblr.
SCROLL = 50

DOMAINS_REGEX = re.compile('>([^<]*)<')
DOMAINS_SPLIT_REGEX = re.compile(',\s*')

def get_domains(limit, offset):
    posts = tumblr_client.posts('plaintextoffenders.com', limit = limit, offset = offset)['posts']
    return set(chain.from_iterable(extract_domains(post) for post in posts))

def extract_domains(post):
    caption = post['caption']
    domains = DOMAINS_SPLIT_REGEX.split(DOMAINS_REGEX.search(caption).group(1))
    return map(encode_domain, domains)

def encode_domain(str):
    return str.encode('utf-8').strip().replace('\xa0', '').replace('\xc2', '')

def write_domains(potential_domains, existing_domains):
    with open(DOMAINS_FILENAME, 'a') as f:
        for domain in potential_domains - existing_domains:
            if domain:
                f.write(domain + '\n')

if __name__ == '__main__':
    keys = [l.strip() for l in open(KEYS_FILENAME).readlines()]
    existing_domains = set([l.strip() for l in open(DOMAINS_FILENAME).readlines()])
    tumblr_client = pytumblr.TumblrRestClient(consumer_key = keys[0], consumer_secret = keys[1])

    for i in range(0, LIMIT / SCROLL):
        domains = get_domains(SCROLL, i * SCROLL)
        write_domains(domains, existing_domains)
