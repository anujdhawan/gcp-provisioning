
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
from googleapiclient import errors
import argparse

#Variables
admin_email = '' #Google Admin Console User email
SERVICE_ACCOUNT_EMAIL = '' #Email of the Service Account
SERVICE_ACCOUNT_JSON_FILE_PATH = '' #Path to the Service Account's Private Key file

#Arguments
parser = argparse.ArgumentParser(description='Checks if user has Cloud Identity')
parser.add_argument('useremail', type=str, help='Email address of user to check')
args = parser.parse_args()

user = args.useremail

def create_directory_service(user_email):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        SERVICE_ACCOUNT_JSON_FILE_PATH,
        scopes=['https://www.googleapis.com/auth/admin.directory.user',
                'https://www.googleapis.com/auth/admin.directory.group'])

    credentials = credentials.create_delegated(user_email)

    return build('admin', 'directory_v1', credentials=credentials)

service = create_directory_service(admin_email)

request = service.users().get(userKey=user)
try:
    response = request.execute()
except errors.HttpError as err:
    print("Error: User does not exist.")
else:
    pprint(response)
