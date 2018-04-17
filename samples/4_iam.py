#!/bin/bash

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import argparse
from os import environ

#Variables
service_account_json_file_path = ''

#Arguments
parser = argparse.ArgumentParser(description='Link billing account')
parser.add_argument('project_id', type=str, help='Project ID to link to billing account')
parser.add_argument('userlist', type=str, help='Email address of users to check')
parser.add_argument('-g', '--grouplist', type=str, help='Email address of AD groups to check')
args = parser.parse_args()

#Set environment variable for service account authorization
environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_json_file_path

#The code below is utilized to provision the project
credentials = GoogleCredentials.get_application_default()
service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)

#Testing setting IAM Permissions
service_account_string = 'serviceAccount:'
user_string = 'user:'
group_string = 'group:'


userlist = args.userlist
grouplist = args.grouplist


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
if grouplist:
    groups = create_email_list(grouplist)
project_id = args.project_id


set_iam_policy_request_body = {
        'policy': {
            'bindings': [
                {
                    'members': [
                        ],
                    'role': 'roles/owner'
                }
                ]
            }
        }

if users != []:
    for name in users:
        (set_iam_policy_request_body['policy']['bindings'][0]['members']).append(user_string+name)

if grouplist:
    if groups != []:
        for set in groups:
            (set_iam_policy_request_body['policy']['bindings'][0]['members']).append(group_string+set)


iam_request = service.projects().setIamPolicy(resource=project_id, body=set_iam_policy_request_body)
iam_response = iam_request.execute()
print("Project ownership has been granted to requested users and groups")
