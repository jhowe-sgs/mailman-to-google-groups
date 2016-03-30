#!/usr/bin/python

# A quick hack on the "Google Apps Groups Migration API Quickstart" program
#
# Giving a Google Group, walk through the legacy Mailman mbox file
# and extract only the text/plain part
#
# Many scripts walk through the mbox and just forward to the google group
# however, that doesn't preserve the original time stamp
#
# multiple runs on the mbox are idempotent since Messages-ID is constant
#
# At some point I may loop back to figure out how to do multi-part preservation
# passes since some e-mails had PDFs, M$ docs, etc.
#
# Mac OS X 10.10.5 requires the sys.path.insert hack to work 
#

from __future__ import print_function

import sys
sys.path.insert(1, '/Library/Python/2.7/site-packages')

# from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import apiclient
from email import Utils
from email import MIMEText
import StringIO
import random
import mailbox
import datetime
from email import utils
from email import MIMEText

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/groupsmigration-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/apps.groups.migration'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Apps Groups Migration API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'groupsmigration-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Google Admin-SDK Groups Migration API.

    Creates a Google Admin-SDK Groups Migration API service object and
    inserts a test email into a group.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('groupsmigration', 'v1', http=http)

    groupId = raw_input(
        'Enter the email address of a Google Group in your domain: ')

    mbox_in = raw_input('Name of mbox to migrate: ')

    src_mbox = mailbox.mbox(mbox_in)
    msg_count = 1
    msg_total = len(src_mbox)

    for msg in src_mbox:
        if msg.is_multipart():
            found = 0
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    found = 1
                    message = MIMEText.MIMEText(part.get_payload())
            if not found:
                print('Error! No text/plain part found!')
		continue
        else:
            message = MIMEText.MIMEText(msg.get_payload())

        message['Message-ID'] = msg['Message-ID']
        message['Subject'] = msg['Subject']
        message['From'] = msg['From']
        message['To'] = groupId
        message['Date'] = msg['Date']

        stream = StringIO.StringIO()
        stream.write(message.as_string())
        media = apiclient.http.MediaIoBaseUpload(stream,
                                             mimetype='message/rfc822')

        result = service.archive().insert(groupId=groupId,
                                      media_body=media).execute()

        if result['responseCode'] != 'SUCCESS':
            print('Issue with Message # ', msg_count, ' Message-ID: ', msg['Message-ID'], 'Reponse Code: ', result['responseCode'])
        else:
            print('Working on msg: ', msg_count, ' out of ', msg_total)

	msg_count += 1

if __name__ == '__main__':
    main()
