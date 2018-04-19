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
import json
import logging
import logging.config


#Variables
org_id = '852670763926' #12-digit GCP organization ID number (string)
service_account_json_file_path = '/home/pi/scripts/key.json' #Local path to service account's JSON key
admin_email='travissamuel@tsam184.com' #Email address of Google Admin Console Super Admin
billing_account_id = '01BC14-B7E869-35B603' #18-character org billing id

#Set environment variable to use JSON file for service account authorization
environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_json_file_path


def errorParser(errorCode):
    try:
        myvars = {}
        with open("errorList.txt") as myfile:
            for line in myfile:
                name, var = line.partition("=")[::2]
                myvars[name.strip()] = var.strip()
            if errorCode in myvars:
                errorReason = myvars[errorCode]
            else:
                errorReason = myvars["DEFAULT_MESSAGE"]
    except Exception as ex:
        return {'ReturnCode': 'Error' , 'ErrorMessage' : "Error Creating AWS account"}
    return errorReason



def main():
    parser = argparse.ArgumentParser(description='Provision new GCP Project')
    parser.add_argument('--project_name', type=str, help='Name of project')
    parser.add_argument('--lifecycle', type=str, help='Lifecycle or environment of project')
    parser.add_argument('--user_list', type=str, help='List of users to grant project ownership')
    parser.add_argument('--group_list', type=str, help='Optional list of groups to grant project ownership')
    parser.add_argument('--department_code', type=str, help='Department Code')
    args = vars(parser.parse_args())

    with open('logging.json', 'r') as f:
        configInfo = json.load(f)
        logging.config.dictConfig(configInfo)

    logger = logging.getLogger(__name__)


    userlist = check_cloud_identity.create_email_list(args['user_list'])
    users = check_cloud_identity.check_user_cloud_identity(userlist, admin_email, service_account_json_file_path)
    if users['existing'] != []:
        iam_user_list = set_gcp_iam_permissions.setup_iam_user_list(users['existing'])
    if args['group_list']:
        grouplist = check_cloud_identity.create_email_list(args['group_list'])
        groups = check_cloud_identity.check_group_cloud_identity(grouplist, admin_email, service_account_json_file_path)
        if groups['existing'] != []:
            iam_group_list = set_gcp_iam_permissions.setup_iam_group_list(groups['existing'])

    try:
        project_id = create_gcp_project.create_project_id(args['project_name'], args['lifecycle'])
    except Exception as ex:
        logger.error(ex.args, exc_info=True)
        message = {'ReturnCode': 'Error' , 'ErrorMessage' : errorParser(''.join(ex.args))}
        return json.dumps(message)

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
            logger.error('Project creation request does not contain users or groups with valid Cloud Identities')
            raise Exception('EMPTY_USERS_AND_GROUPS')
            message = {'ReturnCode': 'Error' , 'ErrorMessage' : 'EMPTY_USERS_AND_GROUPS'}
            return json.dumps(message)
            exit(5)
    else:
        if users['existing'] != []:
            provisioning_list = iam_user_list
        else:
            logger.error('Project creation request does not contain users with valid Cloud Identities')
            raise Exception('EMPTY_USERS')
            message = {'ReturnCode': 'Error' , 'ErrorMessage' : 'EMPTY_USERS'}
            return json.dumps(message)
            exit(6)


    #Project creation script will return a new project ID in case the original one was already in use
    project_id = create_gcp_project.create_project(args['project_name'], project_id, org_id, args['department_code'], args['lifecycle'])

    count = 15
    while count > 0:
        try:
            set_gcp_iam_permissions.set_iam_policy(project_id, provisioning_list)
            break
        except:
            sleep(3)
            count = count - 1
            if count == 0:
                logger.error('Time out while attempting to grant ownership to proeject: %s' % project_id)
                raise Exception('IAM_TIMEOUT')
                message = {'ReturnCode': 'Error' , 'ErrorMessage' : 'IAM_TIMEOUT'}
                return json.dumps(message)
                exit(7)

    link_billing_account.link_billing(project_id, billing_account_id)

    print("Project: %s has been provisioned" % project_id)

if __name__ == "__main__":
    main()
#    sys.exit(main(sys.argv[1:]))
