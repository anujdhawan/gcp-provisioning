#!/bin/bash

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import errors
import argparse

#Variables
admin_email = '' #Google Admin Console User email
service_account_json_file_path = '' #Path to the Service Account's Private Key file

#Arguments
parser = argparse.ArgumentParser(description='Checks if user has Cloud Identity')
parser.add_argument('userlist', type=str, help='Email address of users to check')
parser.add_argument('grouplist', type=str, help='Email address of AD groups to check')
args = parser.parse_args()

userlist = args.userlist
grouplist = args.grouplist

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

users = create_email_list(userlist)
groups = create_email_list(grouplist)

existing_users = []
non_existent_users = []
existing_groups = []
non_existent_groups = []
service = create_directory_service(admin_email)

for user in users:
    try:
        request = service.users().get(userKey=user)
        response = request.execute()
    except errors.HttpError:
        non_existent_users.append(user)
    else:
        existing_users.append(user)

if non_existent_users != []:
    print('The following users do not exist in Cloud Identity:')
    for user in non_existent_users:
        print(user)

for group in groups:
    try:
        request = service.groups().get(groupKey=group)
        response = request.execute()
    except errors.HttpError:
        non_existent_groups.append(group)
    else:
        existing_groups.append(group)

if non_existent_groups != []:
    print('The following groups do not exist in Cloud Identity:')
    for group in non_existent_groups:
        print(group)
