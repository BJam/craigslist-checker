import os

#Gmail Credentials as environment variables
email = dict(
    username = os.environ['GMAIL_USERNAME'],
    password = os.environ['GMAIL_PASSWORD']
)

#Email to SMS gateway for provider
email_to_sms_gateway = '@vtext.com'

#Phone number as environment variable
phone_number = os.environ['PHONE_NUMBER']

#Base URL for query
base_url = "http://portland.craigslist.org"
