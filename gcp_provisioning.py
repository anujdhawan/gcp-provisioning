#!/bin/bash

from googleapiclient import discovery
from googleapiclient import errors
from oauth2client.client import GoogleCredentials
from oauth2client.service_account import ServiceAccountCredentials
import argparse
from random import choice
from sys import exit
from time import sleep
from os import environ


#Variables
org_id = 'XXXXXXXXXXXX' #12-digit GCP organization ID number (string)
service_account_json_file_path = '/home/pi/scripts/key.json' #Local path to service account's JSON key
admin_email='XXXX@XX.com' #Email address of Google Admin Console Super Admin
billing_account_id = 'XXXXXX-XXXXXX-XXXXXX' #18-character org billing id

#Arguments
parser = argparse.ArgumentParser(description='Provision new GCP Project')
parser.add_argument('project_name', type=str, help='Name of project')
parser.add_argument('lifecycle', type=str, help='Lifecycle or environment of project')
parser.add_argument('userlist', type=str, help='List of users to grant project ownership')
parser.add_argument('-g', '--grouplist', type=str, help='Optional list of groups to grant project ownership')
parser.add_argument('department_code', type=str, help='Department Code')
args = parser.parse_args()

#Parser variables
userlist = args.userlist
grouplist = args.grouplist
project_name = args.project_name
lifecycle = args.lifecycle.lower()
dept_num = args.department_code

#Set environment variable to use JSON file for service account authorization
environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_json_file_path


#1. CONFIRM THAT USERS (AND OPTIONALLY GROUPS) HAVE A CLOUD IDENTITY. IF NOT, EXIT PROGRAM.

def create_directory_service(user_email):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        service_account_json_file_path,
        scopes=['https://www.googleapis.com/auth/admin.directory.user',
                'https://www.googleapis.com/auth/admin.directory.group'])
    credentials = credentials.create_delegated(user_email)
    return discovery.build('admin', 'directory_v1', credentials=credentials)

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
existing_users = []
non_existent_users = []
existing_groups = []
non_existent_groups = []


identity_service = create_directory_service(admin_email)


for user in users:
    try:
        user_request = identity_service.users().get(userKey=user)
        user_response = user_request.execute()
    except errors.HttpError:
        non_existent_users.append(user)
    else:
        existing_users.append(user)

if non_existent_users != []:
    print('The following users do not exist in Cloud Identity:')
    for user in non_existent_users:
        print(user)

if grouplist:
    for group in groups:
        try:
            group_request = identity_service.groups().get(groupKey=group)
            group_response = group_request.execute()
        except errors.HttpError:
            non_existent_groups.append(group)
        else:
            existing_groups.append(group)

if non_existent_groups != []:
    print('The following groups do not exist in Cloud Identity:')
    for group in non_existent_groups:
        print(group)

proceed = True
if grouplist:
    if existing_users == [] and existing_groups == []:
        proceed = False
elif existing_users == []:
    proceed = False

if proceed == False:
    print("Error: No valid Users or Groups exist in Cloud Identity. Canceling request.")
    exit(1)
else:
    print("User and group check complete. Continuing.")





#2. CHECK IF PROJECT NAME MEETS NAMING STANDARDS
if len(project_name) < 4 or len(project_name) > 30:
    print("Error: Project name must be between 4 and 30 characters")
    exit(2)


def create_project_id(name, environment):
    prefix = name.lower().strip().lstrip()
    alphanumeric = True
    if not prefix[0].isalpha():
        print("Error: The Project Name must begin with a letter")
        exit(3)
    else:
        for letter in prefix:
            if not (letter.isalnum() or letter.isspace() or letter == "-"):
                alphanumeric = False

    if alphanumeric == False:
        print("Error: The provided Project Name must contain only letters, numbers, spaces, or hyphens")
        exit(4)

    prefix = prefix.replace(" ", "-")
    unique = ""
    for i in range(4):
        unique += choice('0123456789abcdefghijklmnopqrstuvwxyz')
    suffix = "-" + environment.lower() + "-" + unique
    project_id = prefix + suffix

    if len(project_id) > 30:
        overage = len(project_id) - 30
        difference = len(prefix) - overage
        new_prefix = ""
        for i in range(difference):
            new_prefix += prefix[i]
        project_id = new_prefix + suffix

    return project_id

project_id = create_project_id(project_name, lifecycle)





#3. PROVISION GCP PROJECT
credentials = GoogleCredentials.get_application_default()
service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)

project_body = {
        'name': project_name.strip().lstrip(),
        'projectId': project_id,
        'parent': {
            'id': org_id,
            'type': 'organization'
        },
        'labels': {
            'department_code': dept_num,
            'environment': lifecycle
        }
}

count = 10
while count > 0:
    try:
        project_request = service.projects().create(body=project_body)
        project_response = project_request.execute()
    except errors.HttpError:
        print("This project ID is already in use. Trying again...")
        project_id = create_project_id(project_name, lifecycle)
        project_body['projectId'] = project_id
        print("Retrying with Project ID: %s" % project_body['projectId'])
        count = count - 1
        if count == 0:
            print("Unknown http error: Please troubleshoot the project creation loop.")
            exit(5)
    else:
        break

print("Project has been provisioned. Assigning user permissions...")





#4. SET IAM PERMISSIONS
service_account_string = 'serviceAccount:'
user_string = 'user:'
group_string = 'group:'

iam_body = {
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

if existing_users != []:
    for user in existing_users:
        (iam_body['policy']['bindings'][0]['members']).append(user_string+user)

if grouplist:
    if existing_groups != []:
        for group in existing_groups:
            (iam_body['policy']['bindings'][0]['members']).append(group_string+group)

iam_request = service.projects().setIamPolicy(resource=project_id, body=iam_body)


#Assign IAM permissions after project has been created
count = 15
while count > 0:
    try:
        iam_response = iam_request.execute()
    except:
        sleep(2)
    else:
        break

print("Project ownership has been granted. Linking billing account...")





#5. ASSIGN BILLING ACCOUNT TO PROJECT
billing_name = 'projects/' + project_id
billing_body = {
        'name': 'projects/' + project_id + '/billingInfo',
        'projectId': project_id,
        'billingAccountName': 'billingAccounts/' + billing_account_id,
        'billingEnabled': False
        }
billing_service = discovery.build('cloudbilling', 'v1', credentials=credentials)
billing_request = billing_service.projects().updateBillingInfo(name=billing_name, body=billing_body)
billing_response = billing_request.execute()
print("Billing account has been linked. Project %s is now ready for use." % project_id)
