#!/bin/bash

from googleapiclient import discovery
from googleapiclient import errors
from oauth2client.client import GoogleCredentials
import argparse
from random import choice
from sys import exit
from time import sleep
from os import environ #TEMPORARILY SETTING AUTHORIZATION LOCATION
from pprint import pprint #FOR TESTING. REMOVE FROM FINAL VERSION

parser = argparse.ArgumentParser(description='Link billing account')
parser.add_argument('project_id', type=str, help='Project ID to link to billing account')
args = parser.parse_args()

#Imported variables
#Project Name
#Project Lifecycle

#Hardcoded variables
org_id = ''
service_account = ''

#TEST
project_name = "Label Test"
lifecycle = "PROD"
dept_num = "123456"

#Temporarily adding environment variable for service account authorization
environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/pi/scripts/key.json'

#The code below is utilized to provision the project
credentials = GoogleCredentials.get_application_default()
service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)

#Testing setting IAM Permissions
service_account_string = 'serviceAccount:'
user_string = 'user:'
group_string = 'group:'


project_id = args.project_id
emails = ['nsamuel@tsam184.com', 'dsamuel@tsam184.com']
groups = ['test@tsam184.com']

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

for name in emails:
    (set_iam_policy_request_body['policy']['bindings'][0]['members']).append    (user_string+name)
for set in groups:
    (set_iam_policy_request_body['policy']['bindings'][0]['members']).append        (group_string+set)


iam_request = service.projects().setIamPolicy(resource=project_id, body=set_iam_policy_request_body)
iam_response = iam_request.execute()
pprint(iam_response)




