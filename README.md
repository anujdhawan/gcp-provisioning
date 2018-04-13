# GCP-Provisioning

The purpose of this project is to create Google Cloud Platform (GCP) projects under a defined Organization node. The project performs the following steps to provision a functional GCP project:

1. Checks that a list of users and/or groups that will be given ownership of the provisioned project have valid entries in Cloud Identity.
2. Creates a custom, unique Project ID based on a provided Project Name.
3. Creates the project under the defined Organization node.
4. Grants project ownership to the validated lists of users and/or groups.
5. Links the project to a defined Billing Account.

## Prerequisites

The following elements are required for this project to run:

1. Python 2 must be installed on the hosting machine
  * These scripts were designed for Python 2 and may not work with Python 3
2. The user must have Organization level permissions on the GCP Organization node
3. The user must have access to an "Admin" GCP project with the following APIs enabled:
  * Cloud Resource Manager API
  * Cloud Billing API
  * Admin SDK API
4. The user must have access to view Users and Groups within the Organization's Google Admin Console.
5. The Google API Python Client must be installed on the hosting machine
6. A service account must be provisioned in the "Admin" GCP project
7. Access to a valid GCP Billing Account

## Getting Started
### 1. Setting up your GCP environment

The user should provision a project within GCP that will serve as an "Admin" project. This project will contain the resources and settings required to use the scripts developed in this project.

#### Create Admin Project
Log in to the [Google Cloud Console](https://console.cloud.google.com/). Click the arrow next to the name of your current project near the top of the screen and click the **Create Project** button at the top of the menu. Note that the button is shaped like a "+" sign.

On the next screen, select a desired name for the project (which will be referred to as the "Admin Project" for the remainder of this documentation) and click the **Create** button

#### Enabling APIs

Log in to your Admin Project. Navigate to **APIs & Services > Dashboard**. Then click the **ENABLE APIS AND SERVICES** link near the top of the page to navigate to the API Library.

On the API Library page, search for the following APIs in succession:
1. Cloud Resource Mangaer API
2. Cloud Billing API
3. Admin SDK

After locating each API, click on the tile corresponding to the API and click the "Enable" button if it has not already been enabled. Please note that there will be a "Manage" button instead if the API has already been enabled.

#### Setting up Service Account
##### Creating the Service Account
A service account will be required to make the API calls defined in the project scripts. To create a service account, log into your Admin Project and navigate to **IAM & admin > Service accounts**. Click the **CREATE SERVICE ACCOUNT** near the top of the page.

On the next menu, select a name for your service account (which will be referred to as the "Service Account" for the remainder of this documentation).
You do not need to select a role for the Service Account but select the **Furnish a new private key** checkbox (make sure to select JSON for the key type) and check the **Enable G Suite Domain-wide Delegation** checkbox and click the **Create** button. Make sure to keep the JSON key in a safe location. In addition, take note of the full Service Account name (in the form of an email address).

##### Grant GCP Permissions to Service Account
Log in to the Organization node for your domain in the GCP Console and navigate to **Iam & admin > IAM**. Click the **ADD** link near the top of the page. Enter the full Service Account name and grant the following roles:
1. Resource Manager > Project Creator
2. Resource Manager > Project IAM Admin
3. Billing > Billing Account Administrator

**Note:** The Billing Account Adminstrator role grants more permissions than the Service Account actually needs. If you would like to create a custom role that is limited to the necessary permissions, navigate to **IAM & admin > Roles** within your organization node. Click the **CREATE ROLE** link near the top of the page. Add a Title, Descrption, and ID for the role and select the appropriate Role launch stage. Add the following permissions:

* billing.resourceAssociations.create
* resourcemanager.projects.createBillingAssignment
* billing.resourceAssociations.delete
* resourcemanager.projects.deleteBillingAssignment

##### Grant Admin Console Permissions to the Service Account
Log in to the [Google Admin Console](https://admin.google.com). Navigate to **Security > Settings**.

1. Expand the **API reference** section and ensure that the **Enable API access** checkbox is checked.
2. Expand the **Advanced settings** section and click the **Manage API client access** link
*Enter the client ID of your Service Account in the "Client Name" field
**The client ID can be located by logging in to your Admin project and navigating to **APIs & Services > Credentials**
*Enter the following scopes (ensuring that they're entered in a single, comma-separated line), then click **Authorize**:

      https://www.googleapis.com/auth/admin.directory.user, https://www.googleapis.com/auth/admin.directory.group

### 2. Installing Python 2



### 3. Install Google API Python Client
It is recommended to install the Google API Python Client using PIP. If PIP is not installed on your hosting machine, you can install it by issuing the following command:

      sudo apt-get install python-pip

Once PIP is installed, you can install the Google API Python Client by entering the following command:

      sudo pip install --upgrade google-api-python-client

If you have any issues installing the client or do not want to use PIP, you can find additional information on installation [here](https://developers.google.com/api-client-library/python/start/installation)


## Testing the Project Scripts
### 1. Modules
To aid users in understanding the capabilities of this project, the individual capabilities have been separated and placed in the **samples** folder. Information on each capability is listed below.
#### 1. Cloud Identity Check
This module iterates through provided lists of users and groups to ensure that they are valid users/groups within the Organization's Cloud Identity.
##### Variables
The variables listed below must be set within the 1_identity.py file prior to runtime:

* **admin_email -** This is the email address of a user within your domain that has the ability to view/list users and groups within the Google Admin Console for your organization. Your Service Account acts as this user to verify the user/group information.

* **SERVICE_ACCOUNT_EMAIL -** This is the full name of your Service Account (e.g., fake@projectname.iam.gserviceaccount.com).

* **SERVICE_ACCOUNT_JSON_FILE_PATH -** This is the file path to the JSON key that corresponds to your Service Account. These scripts have been developed with the assumption that the JSON key is stored on the hosting machine. If you would like to store your keys elsewhere, the Credentials section of the script can be modified. Please see [Google's Authentication page] (https://developers.google.com/api-client-library/python/guide/aaa_overview) for further information.

* **names -** A list of user emails that will be checked. The elements of the list must be strings (e.g., names = ['user1@fake.com', 'user2@fake.com']). The list can be empty if you would only like to check groups.

* **groups -** A list of directory groups that will be checked. The elements of the list must be strings (e.g., groups = ['group1@fake.com', 'group2@fake.com']). The list can be empty if you would only like to check user emails.

##### Arguments
The following arguments must be provided when calling the script:

**NONE**

##### Usage
Once the variables are set, run the script by issuing the following command:

      python 1_identity.py

##### Expected Output

The script will output that the list of users/groups are ok, or provide a list of the users/groups that do not exist within your organization's Cloud Identity.

##### Examples

      python 1_identity.py



#### 2. Project ID Creation
This script takes a  project name and lifecycle/environment and creates a corresponding unique project ID which conforms to GCP's naming standards.
##### Variables
The following variables must be set within the 2_project_id.py file prior to runtime:

**NONE**

##### Arguments
The following arguments must be provided when calling the script:
**project_name -** The name of your GCP project. Must be entered as a string.
* **lifecycle -** The project's lifecycle/environment

##### Usage
Once the variables are set, run the script by issuing the following command:

      python 2_project_id.py 'project_name' 'lifecycle'

##### Expected Output

The script will output a project name with a random 4-character alphanumeric string appended to the end.

##### Examples

      python 2_project_id.py 'My Project' 'prod'
      python 2_project_id.py 'Hello WoRlD Project' 'Dev'

#### 3. Project Provisioning
##### Variables
The following variables must be set within the 3_create.py file prior to runtime:

* **org_id -** The GCP organization number assigned to your domain. This can be found by navigating to the organization node in the project dropdown.

* **service_account -** This is the full name of your Service Account (e    .g., fake@projectname.iam.gserviceaccount.com).

* **SERVICE_ACCOUNT_JSON_FILE_PATH -** This is the file path to the JSON key that corresponds to your Service Account. These scripts have been developed with the assumption that the JSON key is stored on the hosting machine. If you would like to store your keys elsewhere, the Credentials section of the script can be modified. Please see [Google's Authentication page] (https://developers.google.com/api-client-library/python/guide/aaa_overview) for further information.


##### Arguments
The following arguments must be provided when calling the script:

**project_name -** The name of your GCP project. Must be entered as a string

#### Expected Output
The script will provision a project within your GCP Organization. The script will print a response if the script has successfully run.


##### Usage
Once the variables are set, run the script by issuing the following command:

      python 3_create.py 'project_name'

##### Examples

      python 3_create.py 'My New Project'
      python 3_create.py 'eCommerce Site'

#### 4. Setting IAM Permissions
##### Variables
The following variables must be set within the 4_iam.py file prior to runtime:
##### Arguments
The following arguments must be provided when calling the script:
##### Usage
Once the variables are set, run the script by issuing the following command:

#### Expected Output
The listed users and/or groups will be granted the Project Owner role on the provisioned project. The script will print an execution response if the script ran successfully.

##### Examples

#### 5. Link Billing Account
##### Variables
The following variables must be set within the 5_billing.py file prior to runtime:

* **billing_account_id -** The ID of the billing account that you will link to defined projects.

* **SERVICE_ACCOUNT_JSON_FILE_PATH -** This is the file path to the JSON key that corresponds to your Service Account. These scripts have been developed with the assumption that the JSON key is stored on the hosting machine. If you would like to store your keys elsewhere, the Credentials section of the script can be modified. Please see [Google's Authentication page](https://developers.google.com/api-client-library/python/guide/aaa_overview) for further information.

##### Arguments
The following arguments must be provided when calling the script:

* **project_id -** The ID of the project that you would like to link to a billing account

##### Usage
Once the variables are set, run the script by issuing the following command:

      python 5_billing.py 'project_id'

##### Expected Output

##### Examples

      python 5_billing.py 'my-test-project-dev-12nd'

### 2. End to End Test
#### Variables

* **org_id -** The GCP organization number assigned to your domain. This can be found by navigating to the organization node in the project dropdown.

* **service_account -** This is the full name of your Service Account (e.g., fake@projectname.iam.gserviceaccount.com).

* **service_account_json_path -** This is the file path to the JSON key that corresponds to your Service Account. These scripts have been developed with the assumption that the JSON key is stored on the hosting machine. If you would like to store your keys elsewhere, the Credentials section of the script can be modified. Please see [Google's Authentication page](https://developers.google.com/api-client-library/python/guide/aaa_overview) for further information.

* **admin_email -** This is the email address of a user within your domain that has the ability to view/list users and groups within the Google Admin Console for your organization. Your Service Account acts as this user to verify the user/group information.

* **billing_account_id -** The ID of the billing account that you will link to defined projects.

#### Arguments

* **lifecycle -** The project's lifecycle/environment

* **project_name -** The name of your GCP project. Must be entered as a string

* **department -** The department code that the project belongs to

#### Usage
Once the variables are set, run the script by issuing the following command:

      python gcp-provisioning.py 'project_name' 'lifecycle' 'department'

#### Expected Output
The completed script will check lists of users and groups (**FUNCTIONALITY TO BE UPDATED**), creates a project, tags the project with labes for the lifecylce and department code, grants the users and groups ownership of the project, and links the project to a billing account. The script will return an error in the case of any problems, otherwise it will return nothing on a successful run.

#### Examples

     python gcp-provisionng.py 'My Project' 'Dev' '123456'
