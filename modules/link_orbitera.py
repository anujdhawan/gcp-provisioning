import requests
from requests.auth import HTTPBasicAuth
import json
import argparse
import datetime
import logging


#Variables
API = '' #Orbitera key
API_S = '' #Orbitera secret key
company = '' #Company Name
project_id = '' #ID of the GCP project to be linked to Orbitera

#Arguments
"""
parser = argparse.ArgumentParser(description='Links project to Orbitera account')
parser.add_argument('--first_name', type=str, help='First name of the Orbitera customer', required=True)
parser.add_argument('--last_name', type=str, help='Last name of the Orbitera customer', required=True)
parser.add_argument('--email', type=str, help='Email address of the Orbitera customer', required=True)
args = parser.parse_args()
"""

logger = logging.getLogger(__name__)

def main():
    customer_id = create_customer_record(args.email, args.first_name, args.last_name, company)
    orbitera_project_number = create_cloud_account(project_id, args.email)
    cloud_link = assign_cloud_account(orbitera_project_number, customer_id, args.email)

#Create a Customer
def create_customer_record(email_id, first_name, last_name, company, API, API_S):
    customer_request_info= {
            "email": email_id,
            "name": first_name + " " + last_name,
            "company": company
    }
    proceed = True
    r = requests.get('https://orbitera.com/c2m/api/v1/customers/', auth=HTTPBasicAuth(API,API_S))
    response_json = json.loads(r.content)
    temp_list = response_json['data']['customer']
    for i in range(len(temp_list)):
        if temp_list[i]['email'] == email_id:
            proceed = temp_list[i]['id']

    if proceed != True:
        logger.info("Customer: %s already exists in Orbitera. Skipping customer creation..." % email_id)
        return proceed
    else:
        try:
            response = requests.post('https://orbitera.com/c2m/api/v1/customers', auth=HTTPBasicAuth(API,API_S), data = customer_request_info)
            response_json = json.loads(response.content)
            customer_id = response_json['data']['customer'][0]['id']
        except:
            logger.error("Error creating customer: $s in Orbitera" % email_id)
            raise Exception('ORBITERA_USER_FAIL')
        else:
            return customer_id


#Creating Cloud Accounts
def create_cloud_account(project_id,email_id, API, API_S):
    requestbody = {
            "accountNumber": project_id,
            "providerCode": "gcp",
            "email": email_id
    }
    try:
        response = requests.post('https://orbitera.com/c2m/api/v1/cloud-accounts', auth=HTTPBasicAuth(API,API_S), data = requestbody)
        response_json = json.loads(response.content)
        id = response_json['data'] ['cloud_account'][0]['id']
    except:
        logger.error("Error creating cloud account: %s in Orbitera" % project_id)
        raise Exception('ORBITERA_CLOUD_ACCOUNT_FAIL')
    else:
        logger.info("Cloud Account: %s has been provisioned in Orbitera." % id)
        return id


#Assign cloud account to customer record
def assign_cloud_account(cloud_id, customer_id, email_id, API, API_S):
    request_body = {
            "ID": int(cloud_id),
            "customerId": int(customer_id),
            "email": email_id,
            "billingStartDate": datetime.date.today()
    }
    try:
        response=requests.post('https://orbitera.com/c2m/api/v1/cloud-accounts/'+str(cloud_id) +'/assign-customer', auth=HTTPBasicAuth(API,API_S), data = request_body)
    except:
        logger.error("Failed to link Orbitera account: %s to user: %s" % (cloud_id, email_id))
        raise Exception('ORBITERA_LINK')
    else:
        logger.info("Cloud Account: %s has been linked to customer: %s" % (cloud_id, email_id))


if __name__ == '__main__':
    main()
