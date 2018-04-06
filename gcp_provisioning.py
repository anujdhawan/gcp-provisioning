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
from pprint import pprint #FOR TESTING. REMOVE FROM FINAL VERSION


#Client-specific variables. Update these values with those that apply to your organization

org_id = 'XXXXXXXXXXXX' #12-digit GCP organization ID number (string)
service_account = 'XXXX@[project name].gserviceaccount.com' #ID of service account (email address)
service_account_json_path = '/home/pi/scripts/key.json' #Local path to service account's JSON key
admin_email='XXXX@XX.com' #Email address of Google Admin Console Super Admin
billing_account_id = 'XXXXXX-XXXXXX-XXXXXX' #18-character org billing id

#Parser arguments. In addition to these, 2 separate lists containing users and groups (elements of lists are strings) that will be granted project ownership will be added
parser = argparse.ArgumentParser(description='Provision new GCP Project')
parser.add_argument('project_name', type=str, help='Name of project')
parser.add_argument('lifecycle', type=str, help='Lifecycle or environment of project')
parser.add_argument('requester_email', type=str, help='Email of requester')
parser.add_argument('department', type=str, help='Department Code')
args = parser.parse_args()

#Parser variables
user = args.requester_email
project_name = args.project_name
lifecycle = args.lifecycle.lower()
dept_num = args.department

#Set environment variable to use JSON file for service account authorization
environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_json_path

#1. CONFIRM THAT USER HAS CLOUD IDENTITY. IF NOT, EXIT PROGRAM.
def create_directory_service(user_email):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        service_account_json_path,
        scopes=['https://www.googleapis.com/auth/admin.directory.user',
                'https://www.googleapis.com/auth/admin.directory.group'])
    credentials = credentials.create_delegated(user_email)
    return discovery.build('admin', 'directory_v1', credentials=credentials)

identity_service = create_directory_service(admin_email)

identity_request = identity_service.users().get(userKey=user)
try:
    identity_response = identity_request.execute()
except errors.HttpError:
    print("Error: User does not exist in Cloud Identity")
    exit(1)
else:
    pprint(identity_response)



#2. CHECK IF PROJECT NAME MEETS NAMING STANDARDS
if len(project_name) < 4 or len(project_name) > 30:
    print("Error: Project name must be between 4 and 30 characters")
    exit(2)


def create_project_id(name, environment):
    prefix = name.lower().strip().lstrip()
    alphanumeric = True
    if not prefix[0].isalpha():
        print("Error: The Project Name must begin with a letter")
        exit(1)
    else:
        for letter in prefix:
            if not (letter.isalnum() or letter.isspace() or letter == "-"):
                alphanumeric = False

    if alphanumeric == False:
        print("Error: The provided Project Name must contain only letters, numbers, spaces, or hyphens")
        exit(1)

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


#3. CODE TO PROVISION THE ACCOUNT
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

while True:
    try:
        project_request = service.projects().create(body=project_body)
        project_response = project_request.execute()
    except errors.HttpError:
        print("This project ID is already in use. Trying again...")
        project_id = create_project_id(project_name, lifecycle)
        project_body['projectId'] = project_id
        print("Retrying with Project ID: %s" % project_body['projectId'])
    else:
        pprint(project_request)
        pprint(project_response)
        break


#4. SET IAM PERMISSIONS
service_account_string = 'serviceAccount:'
user_string = 'user:'
group_string = 'group:'

#HARDCODED FOR DEMO END TO END TEST. OBTAIN THROUGH PARSER IN FINAL VERSION
emails = ['user1@fake.com', 'user2@fake.com']
groups = ['group@fake.com']

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

for name in emails:
    (iam_body['policy']['bindings'][0]['members']).append(user_string+name)
for set in groups:
    (iam_body['policy']['bindings'][0]['members']).append(group_string+set)

iam_request = service.projects().setIamPolicy(resource=project_id, body=iam_body)

#Assign IAM permissions after project has been created
while True:
    try:
        iam_response = iam_request.execute()
    except:
        sleep(2)
    else:
        pprint(iam_response)
        break



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
pprint(billing_request)
pprint(billing_response)
