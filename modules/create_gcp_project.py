#!/usr/bin/env python

from googleapiclient import discovery
from googleapiclient import errors
from oauth2client.client import GoogleCredentials
import argparse
from random import choice
from sys import exit
from os import environ

#Variables
org_id = '' #Your Organization's GCP ID Number
service_account_json_file_path = '' #Local path to service account's JSON key file
environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_json_file_path


def main():
    parser = argparse.ArgumentParser(description='Creates GCP project')
    parser.add_argument('--project_name', type=str, help='Project name', required=True)
    parser.add_argument('--lifecycle', type=str, help='Project lifecycle/environment', required=True)
    parser.add_argument('--department_code', type=str, help='Project department number', required=True)
    args = parser.parse_args()
    project_id = create_project_id(args.project_name, args.lifecycle)
    create_project(args.project_name, project_id, org_id, args.department_code, args.lifecycle)

def create_project_id(name, environment):
    if len(name) < 4 or len(name) > 30:
        print("Error: Project name must be between 4 and 30 characters")
        exit(2)

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


def create_project(project_name, project_id, org_id, dept_num, environment):
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
                'environment': environment.lower()
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
            count = count -1
            if count == 0:
                print("Unknown http error: Please comment out the except and else statements at the end of this script to troubleshoot")
        else:
            print("Project: %s has been provisioned" % project_id)
            break
    return project_id

if __name__ == "__main__":
    main()
#        sys.exit(main(sys.argv[1:]))
