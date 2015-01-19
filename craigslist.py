from bs4 import BeautifulSoup
from urllib2 import urlopen
from datetime import datetime
import csv
import sys
import os
import smtplib
import config

SEARCH_TERM="/search/sss?query={0}"

def parse_results(search_term):
    results = []
    search_term = search_term.strip().replace(' ', '+')
    search_url = config.base_url + SEARCH_TERM.format(search_term)
    soup = BeautifulSoup(urlopen(search_url).read())
    rows = soup.find('div', 'content').find_all('p', 'row')
    for row in rows:
        # URL
        if ".org" in row.a['href']:
            url = row.a['href']
        else:
            url = config.base_url + row.a['href']
        # Price
        if row.find('span', class_='price'):
            price = row.find('span', class_='price').get_text()
        else:
            price = "N/A"
        # Date
        create_date = row.find('time').get('datetime')
        # Title
        title = row.find_all('a')[1].get_text()
        # Add reult
        results.append({'url': url, 'create_date': create_date, 'title': title, 'price': price})
    return results

def write_results(results):
    """Writes list of dictionaries to file."""
    fields = results[0].keys()
    with open('results.csv', 'w') as f:
        dw = csv.DictWriter(f, fieldnames=fields, delimiter=',')
        dw.writer.writerow(dw.fieldnames)
        dw.writerows(results)

def find_new_records(results):
    current_posts = [x['url'] for x in results]
    fields = results[0].keys()

    with open('results.csv', 'r') as f:
        reader = csv.DictReader(f, fieldnames=fields, delimiter=',')
        seen_posts = [row['url'] for row in reader]

    new_count = 0
    old_count = 0
    for post in current_posts:
        if post in seen_posts:
            old_count +=1
            pass
        else:
            new_count += 1
    return new_count

def send_text(phone_number, msg):
    fromaddr = "Craigslist Checker"
    toaddrs = phone_number + config.email_to_sms_gateway
    msg = ("From: {0}\r\nTo: {1}\r\n\r\n{2}").format(fromaddr, toaddrs, msg)
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(config.email['username'], config.email['password'])
    # server.sendmail(fromaddr, toaddrs, msg)
    server.quit()

def get_current_time():
    return datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    try:
        TERM = sys.argv[1]
        PHONE_NUMBER = config.phone_number.strip().replace('-', '')
    except:
        print "You need to include a search term and a 10-digit phone number!\n"
        sys.exit(1)

    if len(PHONE_NUMBER) != 10:
        print "Phone numbers must be 10 digits!\n"
        sys.exit(1)

    # count results in db
    results = parse_results(TERM)


    # create csv if one does not exist
    if not os.path.exists('results.csv'):
        fields = results[0].keys()
        with open('results.csv', 'w') as f:
            dw = csv.DictWriter(f, fieldnames=fields, delimiter=',')
            dw.writer.writerow(dw.fieldnames)


    # Send the SMS message if there are new results
    new_record_count = find_new_records(results)

    if new_record_count > 0:
        message = "Hey - there are {0} new Craigslist posts for: {1}".format(new_record_count, TERM.strip())
        print "[{0}] There are {1} new results - sending text message to {2}".format(get_current_time(),new_record_count, PHONE_NUMBER)
        send_text(PHONE_NUMBER, message)
        write_results(results)
    else:
        print "[{0}] No new results - will try again later".format(get_current_time())
