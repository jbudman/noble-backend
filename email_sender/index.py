from icecream import ic
import time
import boto3
import os
import email
import json
from utils import *
from properties import *

region = os.environ['REGION']
sqs_client = boto3.client('sqs')

def transmit_email(event, context):

    ic('New message received on queue with type {}'.format(event['email_type']))
    message = create_message(subject=email_template_mapper[event['email_type']]['subject'], body=email_template_mapper[event['email_type']]['subject'],
                             sender=os.environ['SES_EMAIL'], recipient=event['email'])

    ic('Message successfully created for recipient {}'.format(event['email']))

    output = send_email(region=region, message=message)

    ic(output)

    return output