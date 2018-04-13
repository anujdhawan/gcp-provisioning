#!/bin/bash

#This script link's a newly created Google Cloud Platform (GCP) project to
#a predefined billing account.


from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import argparse
from pprint import pprint
from os import environ

#Variables
billing_account_id = '01BC14-B7E869-35B603' #GCP Billing Account ID that project will be linked to
SERVICE_ACCOUNT_JSON_FILE_PATH = '/home/pi/scripts/key.json' #Path to the SErvice Account's Private Key file

#Arguments
parser = argparse.ArgumentParser(description='Links newly created GCP project to billing account')
parser.add_argument('project_id', type=str, help='Project ID to link to billing account')
args = parser.parse_args()

project_id = args.project_id


#Set environment variable for service account authorization
environ['GOOGLE_APPLICATION_CREDENTIALS'] = SERVICE_ACCOUNT_JSON_FILE_PATH
credentials = GoogleCredentials.get_application_default()
service = discovery.build('cloudbilling', 'v1', credentials=credentials)

#Enter the name of the project that will be associated to a billing account
name='projects/' + project_id
project_billing_info_body = {
        'name': 'projects/' + project_id + '/billingInfo',
        'projectId': project_id,
        'billingAccountName': 'billingAccounts/' + billing_account_id,
        'billingEnabled': False
        }
request = service.projects().updateBillingInfo(name=name, body=project_billing_info_body)
response = request.execute()
pprint(request)
pprint(response)
