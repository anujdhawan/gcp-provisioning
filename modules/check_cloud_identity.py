#!/usr/bin/env python

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import errors
import argparse
import sys

#Variables
admin_email = '' #Google Admin Console User email
service_account_json_file_path = '' #Path to the Service Account's Private Key file



def create_directory_service(user_email):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        service_account_json_file_path,
        scopes=['https://www.googleapis.com/auth/admin.directory.user',
                'https://www.googleapis.com/auth/admin.directory.group'])

    credentials = credentials.create_delegated(user_email)

    return build('admin', 'directory_v1', credentials=credentials)


def create_email_list(emails):
    email_list = []
    username = ''

    for character in emails:
        if character.isalnum() or character == '@' or character == '.':
            username = username + character
        elif character == ',' or character == ']':
            email_list.append(username)
            username = ''
    return email_list

def main():
    parser = argparse.ArgumentParser(description='Checks if user has Cloud Identity')
    parser.add_argument('--user_list', type=str, help='Email address of users to check', required=True)
    parser.add_argument('--group_list', type=str, help='Email address of AD groups to check', required=False)
    args = parser.parse_args()

    if args.user_list:
        users = create_email_list(args.user_list)
        user_check = check_user_cloud_identity(users)
    if args.group_list:
        groups = create_email_list(args.group_list)
        group_check = check_group_cloud_identity(groups)



def check_user_cloud_identity(email_list):
    existing_emails = []
    non_existing_emails = []
    service = create_directory_service(admin_email)

    for user in email_list:
        try:
            request = service.users().get(userKey=user)
            response = request.execute()
        except errors.HttpError:
            non_existing_emails.append(user)
        else:
            existing_emails.append(user)

    if non_existing_emails != []:
        print('The following users do not exist in Cloud Identity:')
        for email in non_existing_emails:
            print(email)

    email_dictionary = {'existing': existing_emails, 'non_existent': non_existing_emails}
    return email_dictionary

def check_group_cloud_identity(email_list):
    existing_emails = []
    non_existing_emails = []
    service = create_directory_service(admin_email)

    for group in email_list:
        try:
            request = service.groups().get(groupKey=group)
            response = request.execute()
        except errors.HttpError:
            non_existing_emails.append(group)
        else:
            existing_emails.append(group)

    if non_existing_emails != []:
        print('The following groups do not exist in Cloud Identity:')
        for email in non_existing_emails:
            print(email)

        email_dictionary = {'existing': existing_emails, 'non_existing': non_existing_emails}
        return email_dictionary


if __name__ == "__main__":
    main()
#        sys.exit(main(sys.argv[1:]))
