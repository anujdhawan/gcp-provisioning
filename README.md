# GCP-Provisioning

The purpose of this project is to create Google Cloud Platform (GCP) projects under a defined Organization node. The project performs the following steps to provision a functional GCP project:

1. Checks that a list of users and/or groups that will be given ownership of the provisioned project have valid entries in Cloud Identity.
2. Creates a custom, unique Project ID based on a provided Project Name.
3. Creates the project under the defined Organization node.
4. Grants project ownership to the validated lists of users and/or groups.
5. Links the project to a defined Billing Account.
6. Links the created project to an Orbitera account

Table of Contents
=================
<!--ts-->
  * [Prerequisites](#prerequisites)
  * [Getting Started](#getting-started)
    * [Setting Up Your GCP Environment](#setting-up-your-gcp-environment)
      * [Create Admin Project](#create-admin-project)
      * [Enabling APIs](#enabling-apis)
      * [Setting Up Service Account](#setting-up-service-account)
        * [Creating the Service Account](#creating-the-service-account)
        * [Grant GCP Permissions to Service Account](#grant-gcp-permissions-to-service-account)
        * [Grant Admin Console Permissions to the Service Account](#grant-admin-console-permissions-to-the-service-account)
    * [Installing Python 2](#installing-python-2)
    * [Installing the Google API Python Client](#installing-the-google-api-python-client)
    * [Installing Requests Package](#installing-requests-package)
  * [Using the Project Scripts](#using-the-project-scripts)
    * [Modules](#modules)
      * [Cloud Identity Check](#1-cloud-identity-check)
      * [Project Provisioning](#2-project-provisioning)
      * [Setting IAM Permissions](#3-setting-iam-permissions)
      * [Link Billing Account](#4-link-billing-account)
      * [Link to Orbitera](#5-link-to-orbitera)
    * [Using the Main Script](#using-the-main-script)
    * [Logging](#logging)
    * [Supplementary Scripts](#supplementary-scripts)
      * [Provision New User](#provision-new-user)
<!--te-->


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
6. The Python Requests package must be installed on the hosting machine
7. A service account must be provisioned in the "Admin" GCP project
8. Access to a valid GCP Billing Account
9. Access to an Orbitera account



## Getting Started
### Setting Up Your GCP Environment

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

#### Setting Up Service Account
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

### Installing Python 2

Please see the [Python website](https://www.python.org/downloads/) for information on installing Python 2 for your computer's operating system.

### Installing the Google API Python Client
It is recommended to install the Google API Python Client using PIP. If PIP is not installed on your hosting machine, you can install it by issuing the following command:

      sudo apt-get install python-pip

Once PIP is installed, you can install the Google API Python Client by entering the following command:

      sudo pip install --upgrade google-api-python-client

If you have any issues installing the client or do not want to use PIP, you can find additional information on installation [here](https://developers.google.com/api-client-library/python/start/installation)

### Installing Requests Package

The Python Requests package will be required to make API calls to Orbitera. Information on installing the package can be found on the [Requests site](http://docs.python-requests.org/en/master/user/install/#install)

## Using the Project Scripts
### Modules
To aid users in understanding the capabilities of this project, the individual capabilities have been separated and placed in separate scripts. Information on each capability is listed below.

#### 1. Cloud Identity Check
This module iterates through provided lists of users and groups to ensure that they are valid users/groups within the Organization's Cloud Identity. This functionality is held in the check_cloud_identity.py script.

#### 2. Project Provisioning
This script takes a  project name and lifecycle/environment and creates a corresponding unique project ID which conforms to GCP's naming standards. It then creates the GCP project once it has been confirmed that at least one user or group in the provided lists exists with Cloud Identity. This functionality is held in the create_gcp_project.py script.

#### 3. Setting IAM Permissions
This script will grant project ownership to a defined project ID to the provided users and/or groups once the GCP project has been provisioned. This functionality is held in the set_gcp_iam_permissions.py script.

#### 4. Link Billing Account
This script links the newly provisioned GCP project to a defined billing account. The functionality is held in the link_billing_account.py script.

#### 5. Link to Orbitera
Orbitera is a cloud commerce platform that allows users to monitor their spending on various cloud service providers. This script confirms/creates a customer in Orbitera and links the GCP project to the customer.

### Using the Main Script
The provision_gcp_project_wrapper.py script calls on the other scripts to provision your GCP project, grant ownership, and link it to a billing account.
#### Variables
The following variables must be set within the provision_gcp_project_wrapper.py file prior to runtime:

* **org_id -** The GCP organization number assigned to your domain. This can be found by navigating to the organization node in the project dropdown.

* **service_account_json_file_path -** This is the file path to the JSON key that corresponds to your Service Account. These scripts have been developed with the assumption that the JSON key is stored on the hosting machine. If you would like to store your keys elsewhere, the Credentials section of the script can be modified. Please see [Google's Authentication page](https://developers.google.com/api-client-library/python/guide/aaa_overview) for further information.

* **admin_email -** This is the email address of a user within your domain that has the ability to view/list users and groups within the Google Admin Console for your organization. Your Service Account acts as this user to verify the user/group information.

* **billing_account_id -** The ID of the billing account that you will link to defined projects.

* **API -** This is the API key from your Orbitera account

* **API_S -** This is the secret key from your Orbitera account

* **company -** This is your company's name. This will be set as the organization name when creating the Orbitera customer.

#### Arguments
The following arguments must be provided when calling the script:

* **requester_first_name -** First name of the project requester. Used to create Orbitera customer. Must be entered as a string

* **requester_last_name -** Last name of the project requester. Ussed to create Orbitera customer. Must be entered as a string

* **requester_email -** Email address of the project requester. Used to create Orbitera customer. Must be entered as a string

* **project_name -** The name of your GCP project. Must be entered as a string

* **lifecycle -** The project's lifecycle/environment

* **user_list -** A list of user emails that will be checked. The list must encompassed by brackets (e.g., names = [user1@fake.com, user2@fake.com]).

* **group_list -** A list of directory groups that will be checked. The list must be encompassed by brackets (e.g., groups = [group1@fake.com, group2@    fake.com]). The group list is optional.

* **department_code -** The department code that the project belongs to

#### Usage
Once the variables are set, run the script by issuing the following command:

      python provision_gcp_project_wrapper.py [-h] --requester_first_name REQUESTER_FIRST_NAME --requester_last_name REQUESTER_LAST_NAME --requester_email REQUESTER    _EMAIL --project_name PROJECT_NAME --lifecycle LIFECYCLE --user_list USER_LIST [--group_list GROUP_LIST] --department_code DEPARTMENT_CODE

#### Expected Output
The completed script will check lists of users and groups, creates a project, tags the project with labels for the lifecylce and department code, grants the users and groups ownership of the project, and links the project to a billing account. Upon successful completion, the script will return a message indicating that the project has been provisioned and will provide the project ID. If no message is returned, please check the logs to see what error has occured.

#### Examples

     python provision_gcp_project_wrapper.py --requester_first_name "John" --requester_last_name "Doe" --requester_email "john@fake.com" --project_name "My Project" --lifecycle "Dev" --user_list "[user1@fake.com]"  --department_code "123456"
     python provision_gcp_project_wrapper.py --requester_first_name "Jane" --requester_last_name "Doe" --requester_email "jane@fake.com" --project_name "eCommerce Site" --lifecycle "Prod" --user_list "[user1@fake.com, user2@fake.com]" --group_list "[group@fake.com]" --department_code "234242"

### Logging
The scripts log various events as they run. The debug.log, info.log, and errors.log files will be generated after the first run of the scripts. Please check these files for information on your script runs.

### Supplementary Scripts
The **add_ons** folder of this project will provide additional scripts to provide functionality that is not included in the primary provision_gcp_project_wrapper.py script. The supplementary scripts allow a user to:
    * Provision a new user in Cloud Identity


#### Provision New User
This script can be used to provision a new user within your Organization's Google Admin Console. The script has been designed to run independent of the main provision_gcp_project_wrapper.py file. If you choose to integrate this script with main script, logging can be enabled by uncommenting the appropriate lines in provision_user.py

**WARNING:** If the requested user is a conflicting account, the script will automatically force the user to change the email address associated with their consumer account and does not provide the opportunity to migrate the existing account to your organization. Only use this script for brand new users or accounts for which you want to reclaim without migrating the associated     data to your organization.
#### Variables
The following variables must be set within the provision_user.py file prior to runtime:

* **admin_email -** This is the email address of a user within your domain that has the ability to view/list users and groups within the Google Admin Console for your organization. Your Service Account acts as this user to verify the user/group information.

* **service_account_json_file_path -** This is the file path to the JSON key that corresponds to your Service Account. These scripts have been developed with the assumption that the JSON key is stored on the hosting machine. If you would like to store your keys elsewhere, the Credentials section of the script can be modified. Please see [Google's Authentication page](https://developers.google.com/api-client-library/python/guide/aaa_overview) for further information.

#### Arguments
The following arguments must be provided when calling the script:

* **first_name -** List of first names of the users that you would like to provision. Note that the list must be enclosed by brackets (i.e. "[" and "]")

* **last_name -** List of last names of the users that you would like to provision. Note that the list must be enclosed by brackets (i.e. "[" and "]")

* **email -** List of email addresses of the users that you would like to provision. Note that the list must be enclosed by brackets (i.e. "[" and "]")

* **password -** Optional entry for the password that you would like to provision. If the password is not specified, a random password will be generated.  Note that the list must be enclosed by brackets (i.e. "[" and "]")

#### Usage
Once the variables are set, run the script by issuing the following command:

      python provision_user.py [-h] --first_name FIRST_NAME --last_name LAST_NAME --email EMAIL [--password PASSWORD]


#### Expected Output
The requested user(s) will be provisioned in your Organization's Cloud Identity. The script will print a confirmation message containing the users' email addresses and temporary passwords once the users are successfully provisioned. **NOTE:** If passwords were not specified, the confirmation will be the only way to get the temporary passwords. Please make note of these passwords and pass them to the new users. If you do not note the passwords, they can be manually reset within the Google Admin Console

#### Examples
      python provision_user.py --first_name "[John]" --last_name "[Doe]" --email "[johndoe@fake.com]" --password "[1l1k3appl35]"
      python provision_user.py --first_name "[Charles,Scott]" --last_name "[Xavier,Summers]" --email "[profx@fake.com,cyclops@fake.com]"

