#!/bin/bash

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
from googleapiclient import errors
import argparse


#This script can be used to check if a single group exists in Cloud Identity


#Variables
admin_email = '' #Google Admin Console User email
service_account_json_file_path = '' #Path to the Service Account's Private Key file

#Arguments
parser = argparse.ArgumentParser(description='Checks if user has Cloud Identity')
parser.add_argument('group', type=str, help='Email address of user to check')
args = parser.parse_args()

group = args.group

def create_directory_service(user_email):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        service_account_json_file_path,
        scopes=['https://www.googleapis.com/auth/admin.directory.user',
                'https://www.googleapis.com/auth/admin.directory.group'])

    credentials = credentials.create_delegated(user_email)

    return build('admin', 'directory_v1', credentials=credentials)


service = create_directory_service(admin_email)

try:
    request = service.groups().get(groupKey=group)
    response = request.execute()
except errors.HttpError:
    print("The group does not exist within Cloud Identity.")
else:
    print("Group: %s exists within Cloud Identity." % group)

