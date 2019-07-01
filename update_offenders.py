#!/usr/bin/python

import pytumblr
import re
import unicodecsv as csv
from datetime import datetime

# Domains filename. Assumes csv file where each line contains: domain,post_url,post_date
DOMAINS_FILENAME = '../plaintextoffenders/offenders.csv'
# Tumblr keys filename. Assumes first line is consumer key and second line is consumer secret.
KEYS_FILENAME = 'tumblr_keys'
# Reformed offenders filename. Assumes csv file where each line contains: domain,post_url,post_date
REFORMED_FILENAME = '../plaintextoffenders/reformed.csv'
# Limit number of posts to fetch from Tumblr.
LIMIT = 100
# Scroll size of each request from Tumblr.
SCROLL = 50

DOMAINS_REGEX = re.compile('>([^<]*)<')
DOMAINS_SPLIT_REGEX = re.compile(',\s*')

keys = [l.strip() for l in open(KEYS_FILENAME).readlines()]
tumblr_client = pytumblr.TumblrRestClient(consumer_key=keys[0], consumer_secret=keys[1])


def get_offenders(limit, offset):
    posts = tumblr_client.posts('plaintextoffenders.com',
                                limit=limit, offset=offset)
    all_posts = []
    for post in posts.get('posts', []):
        # Parse post returns a list of dicts. Need to be appended into the all_posts list.
        all_posts += parse_post(post)
    return all_posts


def parse_post(post):
    """
    :param post: Post from Tumblr
    :return: list of dicts - (domain, post_url, post_date_)
    """
    # Parse post url and date
    post_url = post.get('post_url')
    post_date = post.get('date')
    try:
        # Make domains list per post
        post_domains = [{"domain": domain, "post_url": post_url, "post_date": post_date}
                        for domain in get_domains(post)]

        return post_domains

    except Exception as e:
        print('Failed to parse post. Error: {}; Post:'.find(str(e)))
        if 'caption' in post:
            print(post['caption'])
        else:
            print('no caption')
        print(post_url)


def get_domains(post):
    caption = post['caption']
    domains = DOMAINS_SPLIT_REGEX.split(DOMAINS_REGEX.search(caption).group(1))
    return [dm.encode('utf-8').strip().replace('\xa0', '').replace('\xc2', '')
            for dm in domains]


def convert_csv(filename):
    try:
        with open(filename, 'r') as csv_f:
            return list(csv.DictReader(csv_f, fieldnames=['domain', 'post_url', 'post_date']))
    except IOError:
        # File doesn't exist
        return []


def date_less_then(date1, date2):
    dt1 = datetime.strptime(date1, '%Y-%m-%d %H:%M:%S GMT')
    dt2 = datetime.strptime(date2, '%Y-%m-%d %H:%M:%S GMT')
    return dt1 < dt2


def write_domains(offenders, existing_domains, mode='wb'):
    """ Upsert domains in file, using Existing domains and offenders - the latest between them"""
    new_domains = []

    existing_domains_dict = {
        dm.get('domain'): {
            "post_url": dm.get('post_url'),
            "post_date": dm.get('post_date') or '1900-01-01 00:00:00 GMT',
            "domain": dm.get('domain')}
        for dm in existing_domains
    }

    for o in offenders:
        existing_domain = existing_domains_dict.get(o.get('domain'))
        if not existing_domain:
            new_domains.append(o)
        elif date_less_then(existing_domain.get('post_date'), o.get('post_date')):
            new_domains.append(o)
        else:
            new_domains.append(existing_domain)

    with open(DOMAINS_FILENAME, mode=mode) as f:
        writer_ = csv.DictWriter(f, fieldnames=['domain', 'post_url', 'post_date'], lineterminator='\n')
        writer_.writerows(new_domains)


def run():
    existing_domains = convert_csv(DOMAINS_FILENAME)
    existing_domains += convert_csv(REFORMED_FILENAME)

    for i in range(0, LIMIT / SCROLL):
        offenders = get_offenders(SCROLL, i * SCROLL)
        write_domains(offenders, existing_domains, mode='wb' if i == 0 else 'ab')


if __name__ == '__main__':
    run()
