#!/usr/bin/python
# Updates plaintextoffenders domains file based on new posts on the plaintextoffenders.com Tumblr.
import pytumblr
import re
import io
from itertools import chain
from collections import OrderedDict
from datetime import datetime as dt

# Domains filename. Assumes csv file where each line contains: domain,post_url
DOMAINS_FILENAME = '../plaintextoffenders/offenders.csv'
# Tumblr keys filename. Assumes first line is consumer key and second line is consumer secret.
KEYS_FILENAME = 'tumblr_keys'
# Reformed offenders filename. Assumes csv file where each line contains: domain,post_url
REFORMED_FILENAME = '../plaintextoffenders/reformed.csv'
# Limit number of posts to fetch from Tumblr.
LIMIT = 100
# Scroll size of each request from Tumblr.
SCROLL = 50

DOMAINS_REGEX = re.compile('>([^<]*)<')
DOMAINS_SPLIT_REGEX = re.compile(',\s*')

CSV_COLUMN_DOMAIN = 0
CSV_COLUMN_POST_URL = 1
CSV_COLUMN_DATE = 2

def get_offenders(limit, offset):
    posts = tumblr_client.posts('plaintextoffenders.com', limit = limit, offset = offset)['posts']
    return set(chain.from_iterable(parse_post(post) for post in posts))

def parse_post(post):
    try:
        post_url = post['post_url']
        post_date = post['date']
        return map(lambda domain: (domain, post_url, post_date), get_domains(post))
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

def read_domains():
     existing_domains = OrderedDict()
     with io.open(DOMAINS_FILENAME, mode="r", encoding="utf-8-sig") as OFFENDER_FILE:
        for row in OFFENDER_FILE.readlines():
            rowSplit = row.strip().split(',')

            domain = rowSplit[CSV_COLUMN_DOMAIN].encode("utf-8")
            post_url = rowSplit[CSV_COLUMN_POST_URL].encode("utf-8")
            post_date = rowSplit[CSV_COLUMN_DATE]

            if domain not in existing_domains or dateLessThan(existing_domains[domain][1], post_date): # Handling duplicate entries
                existing_domains[domain] = [post_url, post_date]

     return existing_domains

def append_domains(offenders, existing_domains, reformed_domains):
    bChange = False
    for offender in offenders:

        domain = offender[CSV_COLUMN_DOMAIN]
        post_url = offender[CSV_COLUMN_POST_URL]
        post_date = offender[CSV_COLUMN_DATE]

        if domain not in reformed_domains:
            if domain not in existing_domains or dateLessThan(existing_domains[domain][1], post_date): 
                bChange = True
                existing_domains[domain] = [post_url,post_date]

    return bChange

def write_domains(existing_domains):
    with io.open(DOMAINS_FILENAME, mode="w", encoding="utf-8-sig") as f:
        for key in existing_domains:
            post_url = existing_domains[key][0]
            post_date = existing_domains[key][1]
            f.write('{},{},{}\n'.format(key, post_url, post_date).decode("utf-8"))

def first_column_from_csv_file(filename):
    """Returns first column from from csv file."""
    return [l.strip().split(',')[CSV_COLUMN_DOMAIN] for l in open(filename).readlines()]


def dateLessThan(date1,date2):
   dt1 = dt.strptime(date1, '%Y-%m-%d %H:%M:%S %Z')
   dt2 = dt.strptime(date2, '%Y-%m-%d %H:%M:%S %Z')
   return dt1 < dt2

if __name__ == '__main__':
    keys = [l.strip() for l in open(KEYS_FILENAME).readlines()]

    existing_domains = read_domains()
    reformed_domains = first_column_from_csv_file(REFORMED_FILENAME)

    tumblr_client = pytumblr.TumblrRestClient(consumer_key = keys[0], consumer_secret = keys[1])

    bChange = False
    for i in range(0, LIMIT / SCROLL):
        offenders = get_offenders(SCROLL, i * SCROLL)
        bChange = append_domains(offenders, existing_domains, reformed_domains) or bChange
    if bChange:
        write_domains(existing_domains)
    
