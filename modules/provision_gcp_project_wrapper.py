#!/usr/bin/env python

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
import link_orbitera
import json
import logging
import logging.config


#Variables
org_id = '' #12-digit GCP organization ID number (string)
service_account_json_file_path = '' #Local path to service account's JSON key
admin_email='' #Email address of Google Admin Console Super Admin
billing_account_id = '' #18-character org billing id
API = '' #Orbitera key
API_S = '' #Orbitera secret key
company = '' #Company name (e.g., Google)

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
        return {'ReturnCode': 'Error' , 'ErrorMessage' : "Error Creating GCP project"}
    return errorReason


def main():
    parser = argparse.ArgumentParser(description='Provision new GCP Project')
    parser.add_argument('--requester_first_name', type=str, help='First name of the project requester', required=True)
    parser.add_argument('--requester_last_name', type=str, help='Last name of the project requester', required=True)
    parser.add_argument('--requester_email', type=str, help='Email address of project requester', required=True)
    parser.add_argument('--project_name', type=str, help='Name of project', required=True)
    parser.add_argument('--lifecycle', type=str, help='Lifecycle or environment of project', required=True)
    parser.add_argument('--user_list', type=str, help='List of users to grant project ownership', required=True)
    parser.add_argument('--group_list', type=str, help='Optional list of groups to grant project ownership', required=False)
    parser.add_argument('--department_code', type=str, help='Department Code', required=True)
    args = vars(parser.parse_args())

    with open('logging.json', 'r') as f:
        configInfo = json.load(f)
        logging.config.dictConfig(configInfo)

    logger = logging.getLogger(__name__)

    logger.info('Starting GCP project creation process...')

    #Setup lists of users and groups to be given ownership once project is created. Creates groups that do not exist.
    userlist = check_cloud_identity.create_email_list(args['user_list'])
    users = check_cloud_identity.check_user_cloud_identity(userlist, admin_email, service_account_json_file_path)
    iam_user_list = []
    if users['existing'] != []:
        iam_user_list = set_gcp_iam_permissions.setup_iam_user_list(users['existing'])
    if args['group_list']:
        grouplist = check_cloud_identity.create_email_list(args['group_list'])
        groups = check_cloud_identity.check_group_cloud_identity(grouplist, admin_email, service_account_json_file_path)
        if groups['non_existing'] != []:
            for group in groups['non_existing']:
                try:
                    new_groups = check_cloud_identity.create_group(group, admin_email, service_account_json_file_path)
                except Exception as ex:
                    logger.error(ex.args, exc_info=True)
                    message = {'ReturnCode': 'Error', 'ErrorMessage': errorParser(''.join(ex.args))}
                    return json.dumps(message)
                else:
                    sleep(5)
                    try:
                        assigned_users = check_cloud_identity.assign_users(group, users['existing'], admin_email, service_account_json_file_path)
                        groups['existing'].append(group)
                    except Exception as ex:
                        logger.error(ex.args, exc_info=True)
                        message = {'ReturnCode': 'Error', 'ErrorMessage': errorParser(''.join(ex.args))}
                        return json.dumps(message)
        if groups['existing'] != []:
            iam_group_list = set_gcp_iam_permissions.setup_iam_group_list(groups['existing'])

    #Create unique project ID for provisioning
    try:
        project_id = create_gcp_project.create_project_id(args['project_name'], args['lifecycle'])
    except Exception as ex:
        logger.error(ex.args, exc_info=True)
        message = {'ReturnCode': 'Error' , 'ErrorMessage' : errorParser(''.join(ex.args))}
        return json.dumps(message)

    #Consolidate list of users and/or groups that need to be granted project ownership
    if args['group_list']:
        try:
            provisioning_list = check_cloud_identity.combine_lists(users['existing'], groups['existing'], iam_user_list, iam_group_list)
        except Exception as ex:
            logger.error(ex.args, exc_info=True)
            message = {'ReturnCode': 'Error' , 'ErrorMessage' : errorParser(''.join(ex.args))}
            return json.dumps(message)

    else:
        try:
            provisioning_list = check_cloud_identity.single_list(users['existing'], iam_user_list)
        except Exception as ex:
            logger.error(ex.args, exc_info=True)
            message = {'ReturnCode': 'Error' , 'ErrorMessage' : errorParser(''.join(ex.args))}
            return json.dumps(message)

    #Project creation script will return a new project ID in case the original one was already in use
    try:
        project_id = create_gcp_project.create_project(args['project_name'], project_id, org_id, args['department_code'], args['lifecycle'])
    except Exception as ex:
        logger.error(ex.args, exc_info=True)
        message = {'ReturnCode': 'Error' , 'ErrorMessage' : errorParser(''.join(ex.args))}
        return json.dumps(message)

    count = 15
    while count > 0:
        try:
            iam_response = set_gcp_iam_permissions.set_iam_policy(project_id, provisioning_list)
            break
        except:
            sleep(3)
            count = count - 1
            if count == 0:
                try:
                    logger.error('Time out while attempting to grant ownership to proeject: %s' % project_id)
                    raise Exception('IAM_TIMEOUT')
                except Exception as ex:
                    logger.error(ex.args, exc_info=True)
                    message = {'ReturnCode': 'Error' , 'ErrorMessage' : errorParser(''.join(ex.args))}
                    return json.dumps(message)

    #Assign created project to GCP billing account
    try:
        billing_account = link_billing_account.link_billing(project_id, billing_account_id)
    except Exception as ex:
        logger.error(ex.args, exc_info=True)
        message = {'ReturnCode': 'Error' , 'ErrorMessage' : errorParser(''.join(ex.args))}
        return json.dumps(message)

    """
    #Checks to see if customer exists in Orbitera. Creates customer if it doesn't exisst
    try:
        customer_id = link_orbitera.create_customer_record(args['requester_email'], args['requester_first_name'], args['requester_last_name'], company, API, API_S)
    except Exception as ex:
        logger.error(ex.args, exc_info=True)
        message = {'ReturnCode': 'Error' , 'ErrorMessage' : errorParser(''.join(ex.args))}
        return json.dumps(message)

    #Creates cloud account in Orbitera for newly created GCP project
    try:
        orbitera_project_number = link_orbitera.create_cloud_account(project_id, args['requester_email'], API, API_S)
    except Exception as ex:
        logger.error(ex.args, exc_info=True)
        message = {'ReturnCode': 'Error' , 'ErrorMessage' : errorParser(''.join(ex.args))}
        return json.dumps(message)

    #Links cloud account to customer in Orbitera
    try:
        cloud_link = link_orbitera.assign_cloud_account(orbitera_project_number, customer_id, args['requester_email'], API, API_S)
    except Exception as ex:
        logger.error(ex.args, exc_info=True)
        message = {'ReturnCode': 'Error' , 'ErrorMessage' : errorParser(''.join(ex.args))}
        return json.dumps(message)



    print("Project: %s has been provisioned" % project_id)
    """

if __name__ == "__main__":
    main()
