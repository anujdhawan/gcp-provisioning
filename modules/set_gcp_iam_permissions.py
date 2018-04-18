#!/usr/bin/env python

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import argparse
from os import environ
import check_cloud_identity



#Variables
service_account_json_file_path = ''
admin_email = ''

def main():
    parser = argparse.ArgumentParser(description='Link billing account')
    parser.add_argument('--project_id', type=str, help='Project ID to link to billing account', required=True)
    parser.add_argument('--user_list', type=str, help='Email address of users to check', required=True)
    parser.add_argument('--group_list', type=str, help='Email address of AD groups to check', required=False)
    args = parser.parse_args()

    userlist = check_cloud_identity.create_email_list(args.user_list)
    users = check_cloud_identity.check_user_cloud_identity(userlist)
    if users['existing'] != []:
        iam_user_list = setup_iam_user_list(users['existing'])
    if args.group_list:
        grouplist = check_cloud_identity.create_email_list(args.group_list)
        groups = check_cloud_identity.check_group_cloud_identity(grouplist)
        if groups['existing'] != []:
            iam_group_list = setup_iam_group_list(groups['existing'])

    if args.group_list:
        if users['existing'] != [] and groups['existing'] != []:
            provisioning_list = iam_user_list + iam_group_list
        elif groups['existing'] != []:
            provisioning_list = iam_group_list
        elif users['existing'] != []:
            provisioning_list = iam_user_list
    elif users['existing'] != []:
        provisioning_list = iam_user_list

    set_iam_policy(args.project_id, provisioning_list)

#Set environment variable for service account authorization
environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_json_file_path

def setup_iam_user_list(user_email_list):
    iam_user_list = []
    user_string = 'user:'
    for x in user_email_list:
        iam_user_list.append(user_string + x)
    return iam_user_list

def setup_iam_group_list(group_email_list):
    iam_group_list = []
    group_string = 'group:'
    for x in group_email_list:
        iam_group_list.append(group_string + x)
    return iam_group_list

def set_iam_policy(project_id, email_list):
    credentials = GoogleCredentials.get_application_default()
    service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
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

    for email in email_list:
            (set_iam_policy_request_body['policy']['bindings'][0]['members']).append(email)

    iam_request = service.projects().setIamPolicy(resource=project_id, body=set_iam_policy_request_body)
    iam_response = iam_request.execute()
    print("Project ownership has been granted to requested users and groups")

if __name__ == "__main__":
    main()
#        sys.exit(main(sys.argv[1:]))
