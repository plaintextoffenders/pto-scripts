import pytumblr
import re
import io
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
    posts = tumblr_client.posts('plaintextoffenders.com', limit=limit, offset=offset)['posts']
    return set([parse_post(post) for post in posts])


def parse_post(post):
    """
    :param post: Post from Tumblr
    :return: list of dicts - (domain, post_url, post_date_)
    """
    post_url = post.get('post_url')
    post_date = post.get('post_date')
    try:
        if post_date:
            post_date = datetime.strptime(post_date, '%Y%m%dT%H:%M:%S.%f')

        post_domains = [{"domain": domain, "post_url": post_url, "post_date": post_date}
                        for domain in get_domains(post)]

        return post_domains
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
    return [dm.encode('utf-8').strip().replace('\xa0', '').replace('\xc2', '')
            for dm in domains]


def encode_domain(dm):
    return dm.encode('utf-8').strip().replace('\xa0', '').replace('\xc2', '')


def read_domains():
    existing_domains = {}
    with io.open(DOMAINS_FILENAME, mode="r", encoding="utf-8-sig") as offender_file:
        of_reader = csv.DictReader(offender_file, delimiter=',', quotechar='"')
        for row in of_reader:
            domain = row.get('domain')
            post_url = row.get('post_url')
            post_date = datetime.strptime(row.get('post_date'), '%Y-%m-%d %H:%M:%S %Z') if row.get('post_date') \
                else datetime.utcnow()

            if (domain.lower() not in existing_domains or
                    existing_domains.get(domain, {}).get('post_date') <= post_date):
                existing_domains[domain] = {"post_url": post_url, "post_date": post_date}

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
                existing_domains[domain] = [post_url, post_date]

    return bChange


def write_domains(existing_domains):
    with io.open(DOMAINS_FILENAME, mode="w", encoding="utf-8-sig") as f:
        for key in existing_domains:
            post_url = existing_domains[key][0]
            post_date = existing_domains[key][1]
            f.write('{},{},{}\n'.format(key, post_url, post_date).decode("utf-8"))


def convert_csv(filename):
    with open(filename, 'rb') as csv_f:
        return list(csv.DictReader(csv_f))


def dateLessThan(date1, date2):
    dt1 = dt.strptime(date1, '%Y-%m-%d %H:%M:%S %Z')
    dt2 = dt.strptime(date2, '%Y-%m-%d %H:%M:%S %Z')
    return dt1 < dt2


def run():
    existing_domains = read_domains()
    reformed_domains = convert_csv(REFORMED_FILENAME)
    if


if __name__ == '__main__':
    existing_domains = read_domains()
    reformed_domains = first_column_from_csv_file(REFORMED_FILENAME)

    bChange = False
    for i in range(0, LIMIT / SCROLL):
        offenders = get_offenders(SCROLL, i * SCROLL)
        bChange = append_domains(offenders, existing_domains, reformed_domains) or bChange
    if bChange:
        write_domains(existing_domains)
