import pytumblr
import re
import csv
from datetime import datetime
import traceback

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
        parsed_post = parse_post(post)
        if parsed_post:
        	all_posts += parsed_post
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
        print(post)
        post_domains = [{"domain": domain, "post_url": post_url, "post_date": post_date}
                        for domain in get_domains(post)]
        
        return post_domains
    except Exception as e:
        traceback.print_exc()

    except Exception as e:
        print('Failed to parse post. Error: {}; Post:'.find(str(e)))
        if 'caption' in post:
            print(post['caption'])
        else:
            print('no caption')
        print(post_url)


def get_domains(post):
    caption = post['caption']
    return DOMAINS_SPLIT_REGEX.split(DOMAINS_REGEX.search(caption).group(1))


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


def write_domains(offenders, existing_domains, mode='w'):
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
        domain = o.get('domain')
        if domain not in existing_domains_dict:
            new_domains.append(o)
            existing_domains_dict[domain] = o

    with open(DOMAINS_FILENAME, mode=mode) as f:
        writer = csv.DictWriter(f, fieldnames=['domain', 'post_url', 'post_date'], lineterminator='\n')
        print(new_domains)
        writer.writerows(new_domains)


def run():
    existing_domains = convert_csv(DOMAINS_FILENAME)
    existing_domains += convert_csv(REFORMED_FILENAME)

    offenders = []

    for i in range(0, int(LIMIT / SCROLL)):
        offenders += get_offenders(SCROLL, i * SCROLL)

    offenders.reverse()

    write_domains(offenders, existing_domains, mode='a')   

if __name__ == '__main__':
    run()
