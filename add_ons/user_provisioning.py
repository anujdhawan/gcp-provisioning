
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
import argparse
from random import choice


#This script provisions a new user within your organization's Google Admin Console.
#This script can be used to modify the main gcp-provisioning.py script to provision
#a new user if they do not exist in Cloud Identity.


#Variables
SERVICE_ACCOUNT_EMAIL = 'XXXX@[project name].gserviceaccount.com' #ID of service account (email address)
SERVICE_ACCOUNT_JSON_FILE_PATH = '' #Local path to service account's JSON key
admin_email = 'XXXX@XX.com' #Email address of Google Admin Console Super Admin

#Arguments
parser =argparse.ArgumentParser(description='Provisions user in Google Admin Console')
parser.add_argument('firstname', type=str, help="User's first name")
parser.add_argument('lastname', type=str, help="User's last name")
parser.add_argument('email', type=str, help="User's email address")
parser.add_argument('-p', '--password',  type=str, help='Set password for user')
args = parser.parse_args()

#Parser variables
firstname = args.firstname
lastname = args.lastname
email = args.email
password = args.password


def create_directory_service(user_email):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        SERVICE_ACCOUNT_JSON_FILE_PATH,
        scopes=['https://www.googleapis.com/auth/admin.directory.user',
                'https://www.googleapis.com/auth/admin.directory.group'])

    credentials = credentials.create_delegated(user_email)

    return build('admin', 'directory_v1', credentials=credentials)


#Define random password if password flag is not given
if not password:
    password = ""
    for i in range(8):
        password += choice("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_'.")


project_billing_info_body = {
        "name": {
            "familyName": lastname,
            "givenName": firstname
        },
        "password": password,
        "primaryEmail": email,
        "changePasswordAtNextLogin": "true"
}


service = create_directory_service(admin_email)
request = service.users().insert(body=project_billing_info_body)
response = request.execute()
print("User: %s has been created." % email)
