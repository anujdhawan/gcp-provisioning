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

#Imported variables
#Project Name
#Project Lifecycle

#Hardcoded variables
org_id = '852670763926'
service_account = 'project-maker@tsam184-198604.iam.gserviceaccount.com'

#TEST
project_name = "Label Test"
lifecycle = "PROD"
dept_num = "123456"

#Temporarily adding environment variable for service account authorization
environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/pi/scripts/key.json'

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

#The code below is utilized to provision the project
credentials = GoogleCredentials.get_application_default()
service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)

project_body = {
        'name': project_name.strip().lstrip(),
        'projectId': 'iam-test2-121186',
        'parent': {
            'id': org_id,
            'type': 'organization'
        },
        'labels': {
            'department_code': dept_num,
            'environment': lifecycle.lower()
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
