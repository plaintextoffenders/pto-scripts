#!/usr/bin/python
# Updates plaintextoffenders domains file based on new posts on the plaintextoffenders.com Tumblr.

import pytumblr
import re
from itertools import chain

# Domains filename. Assumes csv file where each line contains: domain,post_url
DOMAINS_FILENAME = '../plaintextoffenders/offenders.csv'
# Tumblr keys filename. Assumes first line is consumer key and second line is consumer secret.
KEYS_FILENAME = 'tumblr_keys'
# Limit number of posts to fetch from Tumblr.
LIMIT = 100
# Scroll size of each request from Tumblr.
SCROLL = 50

DOMAINS_REGEX = re.compile('>([^<]*)<')
DOMAINS_SPLIT_REGEX = re.compile(',\s*')

keys = [l.strip() for l in open(KEYS_FILENAME).readlines()]
existing_domains = set([l.strip().split(',')[0] for l in open(DOMAINS_FILENAME).readlines()])

tumblr_client = pytumblr.TumblrRestClient(consumer_key = keys[0], consumer_secret = keys[1])

def get_offenders(limit, offset):
    posts = tumblr_client.posts('plaintextoffenders.com', limit = limit, offset = offset)['posts']
    return set(chain.from_iterable(parse_post(post) for post in posts))

def parse_post(post):
    try:
        post_url = post['post_url']
        return map(lambda domain: '{},{}'.format(domain, post_url), get_domains(post))
    except:
        print 'Failed to parse post:'
        if 'caption' in post:
            print post['caption']
        else:
            print 'no caption'
        print post_url
        return []

def get_domains(post):
    caption = post['caption']
    domains = DOMAINS_SPLIT_REGEX.split(DOMAINS_REGEX.search(caption).group(1))
    return map(encode_domain, domains)

def encode_domain(str):
    return str.encode('utf-8').strip().replace('\xa0', '').replace('\xc2', '')

def write_domains(domains):
    with open(DOMAINS_FILENAME, 'a') as f:
        for domain in domains - existing_domains:
            if domain:
                f.write(domain + '\n')

if __name__ == '__main__':
    for i in range(0, LIMIT / SCROLL):
        domains = get_offenders(SCROLL, i * SCROLL)
        write_domains(domains)
