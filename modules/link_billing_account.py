#!/usr/bin/env python

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import argparse
from os import environ
import logging

logger = logging.getLogger(__name__)

#Variables
billing_account_id = '' #GCP Billing Account ID that project will be linked to
service_account_json_file_path = '' #Path to the SErvice Account's Private Key file

#Set environment variable for service account authorization
environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_json_file_path


def main():
    parser = argparse.ArgumentParser(description='Links newly created GCP project to billing account')
    parser.add_argument('--project_id', type=str, help='Project ID to link to billing account', required=True)
    args = parser.parse_args()

    link_billing(args.project_id, billing_account_id)


def link_billing(project_id, billing_account_id):
    credentials = GoogleCredentials.get_application_default()
    service = discovery.build('cloudbilling', 'v1', credentials=credentials)

    name='projects/' + project_id
    project_billing_info_body = {
            'name': 'projects/' + project_id + '/billingInfo',
            'projectId': project_id,
            'billingAccountName': 'billingAccounts/' + billing_account_id,
            'billingEnabled': False
            }
    request = service.projects().updateBillingInfo(name=name, body=project_billing_info_body)
    response = request.execute()
    logger.info("Project: %s has been linked to Billing Account: %s" % (project_id, billing_account_id))

if __name__ == "__main__":
    main()
#        sys.exit(main(sys.argv[1:]))
