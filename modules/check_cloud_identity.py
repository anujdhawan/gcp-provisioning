#!/usr/bin/env python

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import errors
import argparse
import sys
import logging

logger = logging.getLogger(__name__)

#Variables
admin_email = '' #Google Admin Console User email
service_account_json_file_path = '' #Path to the Service Account's Private Key file


def create_email_list(emails):
    email_list = []
    username = ''

    for character in emails:
        if character.isalnum() or character == '@' or character == '.' or character == '-':
            username = username + character
        elif character == ',' or character == ']':
            email_list.append(username)
            username = ''
    return email_list

def main():
    parser = argparse.ArgumentParser(description='Checks if user has Cloud Identity')
    parser.add_argument('--user_list', type=str, help='Email address of users to check', required=True)
    parser.add_argument('--group_list', type=str, help='Email address of AD groups to check', required=False)
    args = parser.parse_args()

    if args.user_list:
        users = create_email_list(args.user_list)
        user_check = check_user_cloud_identity(users)
    if args.group_list:
        groups = create_email_list(args.group_list)
        group_check = check_group_cloud_identity(groups)
        if group_check['non_existing'] != []:
            for group in group_check['non_existing']:
                create_group(group, admin_email, service_account_json_file_path)
                assign_users(group, user_check['existing'], admin_email, service_account_json_file_path)


def check_user_cloud_identity(email_list, admin_email, service_account_json_file_path):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
            service_account_json_file_path,
            scopes=['https://www.googleapis.com/auth/admin.directory.user',
                    'https://www.googleapis.com/auth/admin.directory.group'])

    credentials = credentials.create_delegated(admin_email)
    service = build('admin', 'directory_v1', credentials=credentials)
    existing_emails = []
    non_existing_emails = []

    for user in email_list:
        try:
            request = service.users().get(userKey=user)
            response = request.execute()
        except errors.HttpError:
            non_existing_emails.append(user)
            logger.warning('User: %s does not exist in Cloud Identity.' % user)
        else:
            existing_emails.append(user)

    email_dictionary = {'existing': existing_emails, 'non_existing': non_existing_emails}
    return email_dictionary

def check_group_cloud_identity(email_list, admin_email, service_account_json_file_path):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
            service_account_json_file_path,
            scopes=['https://www.googleapis.com/auth/admin.directory.user',
                    'https://www.googleapis.com/auth/admin.directory.group'])

    credentials = credentials.create_delegated(admin_email)
    service = build('admin', 'directory_v1', credentials=credentials)
    existing_emails = []
    nonexistingemails = []

    for group in email_list:
        try:
            request = service.groups().get(groupKey=group)
            response = request.execute()
        except errors.HttpError:
            nonexistingemails.append(group)
            logger.warning('Group: %s does not exist in Cloud Identity' % group)
        else:
            existing_emails.append(group)

    email_dictionary = {'existing': existing_emails, 'non_existing': nonexistingemails}
    return email_dictionary


def create_group(group_email, admin_email, service_account_json_file_path):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
            service_account_json_file_path,
            scopes=['https://www.googleapis.com/auth/admin.directory.user',
                    'https://www.googleapis.com/auth/admin.directory.group'])

    credentials = credentials.create_delegated(admin_email)
    service = build('admin', 'directory_v1', credentials=credentials)


    group_request_body = {
        "email": group_email
    }

    request = service.groups().insert(body=group_request_body)
    try:
        response = request.execute()
    except Exception:
        logger.error('Invalid group name syntax')
        raise Exception('INVALID_GROUP_SYNTAX')
    else:
        logger.info("Group: %s has been created." % group_email)


def assign_users(group_email, user_email_list, admin_email, service_account_json_file_path):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
    service_account_json_file_path,
    scopes=['https://www.googleapis.com/auth/admin.directory.user',
            'https://www.googleapis.com/auth/admin.directory.group'])

    credentials = credentials.create_delegated(admin_email)

    service = build('admin', 'directory_v1', credentials=credentials)

    for user in user_email_list:
        user_addition_body = {
                "email": user
        }

        request = service.members().insert(groupKey=group_email, body=user_addition_body)
        try:
            response = request.execute()
        except Exception:
            logger.error('Invalid useri email syntax')
            raise Exception('INVALID_USER_SYNTAX')
        else:
            logger.info("User: %s has been added to the %s group" % (user, group_email))

def combine_lists(list_users, list_groups, list_iam_users, list_iam_groups):
    answer = []
    if list_users != [] and list_groups != []:
        answer = list_iam_users + list_iam_groups
    elif list_groups != []:
        answer = list_iam_groups
    elif list_users != []:
        answer = list_iam_users
    elif list_users != []:
        answer = list_iam_users
    elif list_users == [] and list_groups == []:
        logger.error('Project creation request does not contain users or groups with valid Cloud Identities')
        raise Exception('EMPTY_USERS_AND_GROUPS')
    return answer

def single_list(list_users, list_iam_users):
    answer = []
    if list_users != []:
        answer = list_iam_users
    else:
        logger.error('Project creation request does not contain users with valid Cloud Identities')
        raise Exception('EMPTY_USERS')
    return answer


if __name__ == "__main__":
    main()
#        sys.exit(main(sys.argv[1:]))
