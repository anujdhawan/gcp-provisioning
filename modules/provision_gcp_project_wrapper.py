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
import check_cloud_identity
import create_gcp_project
import link_billing_account
import set_gcp_iam_permissions


#Variables
org_id = '' #12-digit GCP organization ID number (string)
service_account_json_file_path = '' #Local path to service account's JSON key
admin_email='' #Email address of Google Admin Console Super Admin
billing_account_id = '' #18-character org billing id

#Set environment variable to use JSON file for service account authorization
environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_json_file_path


def main():
    parser = argparse.ArgumentParser(description='Provision new GCP Project')
    parser.add_argument('--project_name', type=str, help='Name of project')
    parser.add_argument('--lifecycle', type=str, help='Lifecycle or environment of project')
    parser.add_argument('--user_list', type=str, help='List of users to grant project ownership')
    parser.add_argument('--group_list', type=str, help='Optional list of groups to grant project ownership')
    parser.add_argument('--department_code', type=str, help='Department Code')
    args = vars(parser.parse_args())

    userlist = check_cloud_identity.create_email_list(args['user_list'])
    users = check_cloud_identity.check_user_cloud_identity(userlist, admin_email, service_account_json_file_path)
    if users['existing'] != []:
        iam_user_list = set_gcp_iam_permissions.setup_iam_user_list(users['existing'])
    if args['group_list']:
        grouplist = check_cloud_identity.create_email_list(args['group_list'])
        groups = check_cloud_identity.check_group_cloud_identity(grouplist, admin_email, service_account_json_file_path)
        if groups['existing'] != []:
            iam_group_list = set_gcp_iam_permissions.setup_iam_group_list(groups['existing'])

    project_id = create_gcp_project.create_project_id(args['project_name'], args['lifecycle'])

    if args['group_list']:
        if users['existing'] != [] and groups['existing'] != []:
            provisioning_list = iam_user_list + iam_group_list
        elif groups['existing'] != []:
            provisioning_list = iam_group_list
        elif users['existing'] != []:
            provisioning_list = iam_user_list
        elif users['existing'] != []:
            provisioning_list = iam_user_list
        elif users['existing'] == [] and groups['existing'] == []:
            print("Error: There are no valid users or groups to grant project ownership. Canceling request.")
            exit(1)


    #Project creation script will return a new project ID in case the original one was already taken
    project_id = create_gcp_project.create_project(args['project_name'], project_id, org_id, args['department_code'], args['lifecycle'])
    print(project_id)

    count = 15
    while count > 0:
        try:
            set_gcp_iam_permissions.set_iam_policy(project_id, provisioning_list)
            break
        except:
            sleep(2)
            count = count - 1

    link_billing_account.link_billing(project_id, billing_account_id)

if __name__ == "__main__":
    main()
#    sys.exit(main(sys.argv[1:]))
