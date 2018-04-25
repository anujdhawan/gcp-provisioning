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

#logger = logging.getLogger(__name__)

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

    first_name_list = create_list(args.first_name)
    last_name_list = create_list(args.last_name)
    email_list = create_list(args.email)
    if args.password:
        password_list = create_list(password)

    entry_length = len(first_name_list)
    user_dictionary = {}

    user_body = {
            "name": {
                "familyName": '',
                "givenName": ''
            },
            "password": '',
            "primaryEmail": '',
            "changePasswordAtNextLogin": "true"
    }

    for entry in range(entry_length):
        user_body['name']['familyName'] = last_name_list[entry]
        user_body['name']['givenName'] = first_name_list[entry]
        user_body['primaryEmail'] = email_list[entry]
        if args.password:
            user_body['password'] = password_list[entry]
        else:
            user_body['password'] = random_password()

        try:
            new_user = create_user(user_body, admin_email, service_account_json_file_path)
        except Exception as ex:
            print("Failed to provision user: %s" % user_body['primaryEmail'])
#            logger.error(ex.args, exc_info=True)
#            message = {'ReturnCode': 'Error' , 'ErrorMessage' : errorParser(''.join(ex.args))}
#            return json.dumps(message)
        else:
#            logger.info("User: %s has been created" % user_body['primaryEmail'])
            user_dictionary['user'+str(entry)] = {'email': user_body['primaryEmail'], 'password': user_body['password']}

    pprint(user_dictionary)


def random_password():
    password = ""
    for i in range(8):
        password += choice("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_'.")
    return password

    create_user(args.first_name, args.last_name, args.email, password, admin_email, service_account_json_file_path)


def create_list(entries):
    created_list = []
    username = ''

    for character in entries:
        if character.isalnum() or character == '@' or character == '.' or character == '-':
            username = username + character
        elif character == ',' or character == ']':
            created_list.append(username)
            username = ''
    return created_list


def create_user(json_body, admin_email, service_account_json_file_path):
    credentials =  ServiceAccountCredentials.from_json_keyfile_name(
        service_account_json_file_path,
        scopes=['https://www.googleapis.com/auth/admin.directory.user',
                'https://www.googleapis.com/auth/admin.directory.group'])

    credentials = credentials.create_delegated(admin_email)

    service = build('admin', 'directory_v1', credentials=credentials)

    try:
        request = service.users().insert(body=json_body)
        response = request.execute()
    except:
        print("Failed to create user: %s" % json_body['primaryEmail'])
    else:
        print("User: %s has been created." % json_body['primaryEmail'])
#        logger.info("User: %s has been created." % json_body['primaryEmail'])

if __name__ == "__main__":
    main()
