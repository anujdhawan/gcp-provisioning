
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
from googleapiclient import errors
import argparse

#Client Variables
admin_email = 'travissamuel@tsam184.com' #Google Admin Console User email
SERVICE_ACCOUNT_EMAIL = 'project-maker@tsam184-198604.iam.gserviceaccount.com' #Email of the Service Account
SERVICE_ACCOUNT_JSON_FILE_PATH = '/home/pi/scripts/key.json' #Path to the Service Account's Private Key file

parser = argparse.ArgumentParser(description='Checks if user has Cloud Identity')
parser.add_argument('useremail', type=str, help='Email address of user to check')
args = parser.parse_args()

user = args.useremail

def create_directory_service(user_email):
    """Build and returns an Admin SDK Directory service object authorized
    with the service accounts that act on behalf of the given user.

    Args:
      user_email: The email of the user. Needs permissions to access the
      Admin APIs.
    Returns:
      Admin SDK directory service object.
    """

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
