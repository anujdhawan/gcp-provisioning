#!/usr/bin/env python

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
import argparse
from random import choice
import logging

#This script provisions a new user within your organization's Google Admin Console.
#This script can be used to modify the main gcp-provisioning.py script to provision
#a new user if they do not exist in Cloud Identity.

logger = logging.getLogger(__name__)

#Variables
service_account_json_file_path = '' #Local path to service account's JSON key
admin_email = '' #Email address of Google Admin Console Super Admin

def main():
    parser = argparse.ArgumentParser(description='Provisions user in Google Admin Console')
    parser.add_argument('--first_name', type=str, help="User's first name", required=True)
    parser.add_argument('--last_name', type=str, help="User's last name", required=True)
    parser.add_argument('--email', type=str, help="User's email address", required=True)
    parser.add_argument('--password',  type=str, help='Set password for user', required=False)
    args = parser.parse_args()
    if not args.password:
        password = ""
        for i in range(8):
            password += choice("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_'.")
    else:
        password = args.password

    create_user(args.first_name, args.last_name, args.email, password, admin_email, service_account_json_file_path)


def create_user(firstname, lastname, email, password, admin_email, service_account_json_file_path):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        service_account_json_file_path,
        scopes=['https://www.googleapis.com/auth/admin.directory.user',
                'https://www.googleapis.com/auth/admin.directory.group'])

    credentials = credentials.create_delegated(admin_email)

    service = build('admin', 'directory_v1', credentials=credentials)


    user_info_body = {
            "name": {
                "familyName": lastname,
                "givenName": firstname
            },
            "password": password,
            "primaryEmail": email,
            "changePasswordAtNextLogin": "true"
    }


    request = service.users().insert(body=user_info_body)
    response = request.execute()
    print("User: %s has been created." % email)
    logger.info("User: %s has been created." % email)

if __name__ == "__main__":
    main()
