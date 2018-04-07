#!/usr/bin/python
# Updates plaintextoffenders domains file based on new posts on the plaintextoffenders.com Tumblr.

import subprocess
import whois
import collections
import sys

# Domains filename. Assumes csv file where each line contains: domain,post_url
DOMAINS_FILENAME = '../plaintextoffenders/offenders.csv'
# Emailed domains filename. Assumes each line contains a single domain.
EMAILED_DOMAINS_FILENAME = 'offenders_emailed.txt'
# Limit number of domains to process.
LIMIT = 100

TEMPLATE='''Hello,

This is a message from plaintextoffenders.com - We feature sites that are suspected of insecure handling of user data.
We have received, approved and published a submission from our community that regards your website at {}

Please refer to the submission and evidence here: {}

Please also refer to our FAQs where we answer many of the question you may have:

For non software developers: http://plaintextoffenders.com/faq/non-devs
For software developers: http://plaintextoffenders.com/faq/devs
This issue is grave and we ask that you take it seriously. Please forward this email to the technical person who handles security in your site/organization.

Please note that this is an automated email sent upon publication to attempt to notify you.

Looking forward to hearing back from you.

Plain-Text Offenders'''

def process_domain(domain, post_url):
    try:
        whois_response = whois.whois(domain)
        if 'emails' in whois_response:
            emails = whois_response['emails']
            if emails:
                email(emails, domain, post_url)
            else:
                print 'No emails found for ' + domain
        else:
            print 'No emails found for ' + domain
    except:
        print "Error processing domain:", sys.exc_info()[0]

def email(emails, domain, post_url):
    recipient = emails
    if not isinstance(emails, str):
        recipient = ';'.join(emails)
    print 'Sending email to ' + recipient
    subject = 'Security Vulnerability In Your Site'
    content_type = 'Content-type: text/html;'
    body = TEMPLATE.replace('\n','<br>').format(domain, post_url)
    cmd = 'echo "{}" | mail -s "{}\n{}" "{}"'.format(body, subject, content_type, recipient)
    email_process = subprocess.call(cmd, shell = True)
    if email_process == 0:
        print 'Successfully sent email to ' + recipient
        write_domain(domain)

def write_domain(domain):
    with open(EMAILED_DOMAINS_FILENAME, 'a') as f:
        f.write(domain + '\n')

if __name__ == '__main__':
    existing_domains = list(reversed([l.strip().split(',') for l in open(DOMAINS_FILENAME).readlines()]))
    emailed_domains = set([l.strip() for l in open(EMAILED_DOMAINS_FILENAME).readlines()])

    for existing_domain in existing_domains[0:LIMIT]:
        domain = existing_domain[0]
        post_url = existing_domain[1]
        if domain not in emailed_domains:
            print 'Processing ' + domain
            process_domain(domain, post_url)
            print
