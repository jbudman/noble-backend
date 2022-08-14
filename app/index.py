from connection_scraper import ConnectionScraper
from icecream import ic
import time
import boto3
import os
from utils import HEADLESS_OPTIONS
import email
import json
import connector
from botocore.client import Config

QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/954548076399/email_transmission_queue'

region = os.environ['REGION']
separator = ""
sqs_client = boto3.client('sqs')
db_conn = connector.Connector(region='us')
conn = db_conn.get_connection()
ic('Connection {} established'.format(conn))

def scrape_conns(event,context):
    ic('--initiate scraper in headless mode--')
    file_dict = get_message_from_s3(event)
    mailobject = email.message_from_string(file_dict['file'].decode('utf-8'))
    from_address = mailobject['From']
    message_id = mailobject['Message-ID']

    if 'invitations@linkedin.com' in from_address:
        ic(f"Message ID {message_id} is a LinkedIn invite - initiate scrape process")

        user_full_name = ' '.join(from_address.split(' ')[0:-1])

        ic(user_full_name)
        user_first = user_full_name.split(' ')[0]
        user_last = user_full_name.split(' ')[1]

        # The body text of the email.
        body_text = parse_email(mailobject)

        li_user_url = body_text.split(b'View profile: ')[-1].split(b'\r')[0].decode('utf-8')
        ic(li_user_url)

        user_info_dict = dict()

        with ConnectionScraper() as scraper:
            start = time.time()
            user_email = scraper.scrape_email(url=li_user_url)

            user_info_dict['first_name'] = user_first
            user_info_dict['last_name'] = user_last
            user_info_dict['email'] = user_email
            user_info_dict['email_type'] = 'WELCOME'

            ic(user_info_dict)
            ic('Posting email {} to sqs for new lambda trigger'.format(user_email))
            response = sqs_client.send_message(QueueUrl=os.environ['QUEUE_URL'], MessageBody=json.dumps(user_info_dict))
            ic('Message posted to queue successfully with message ID {}'.format(response['MessageId']))
            scrape_results = scraper.scrape_connections(url=li_user_url)
            end = time.time()

        time_delta = end - start
        ic('Results scraped in {} seconds'.format(time_delta))
        #scrape_results.to_csv('joshua_budman_test_results.csv')

    else:
        ic('Message ID {} not a LinkedIn invited, skipping...'.format(message_id))


def get_message_from_s3(event):

    incoming_email_bucket = os.environ['MAILS3BUCKET']

    object_path = event['Records'][0]['s3']['object']['key']

    object_http_path = (f"http://s3.console.aws.amazon.com/s3/object/{incoming_email_bucket}/{object_path}?region={region}")

    # Create a new S3 client.
    client_s3 = boto3.client("s3",region, config=Config(s3={'addressing_style':'path'}))

    # Get the email object from the S3 bucket.
    object_s3 = client_s3.get_object(Bucket=incoming_email_bucket, Key=object_path)
    # Read the content of the message.
    file = object_s3['Body'].read()

    file_dict = {
        "file": file,
        "path": object_http_path
    }

    return file_dict

def parse_email(email_obj):

    body = ""

    if email_obj.is_multipart():
        for part in email_obj.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))

            # skip any text/plain (txt) attachments
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                body = part.get_payload(decode=True)  # decode
                break
    # not multipart - i.e. plain text, no attachments, keeping fingers crossed
    else:
        body = email_obj.get_payload(decode=True)

    return body