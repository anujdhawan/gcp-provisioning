# GCP-Provisioning

The purpose of this project is to create Google Cloud Platform (GCP) projects under a defined Organization node. The project performs the following steps to provision a functional GCP project:

1. Checks that a list of users and/or groups that will be given ownership of the provisioned project have valid entries in Cloud Identity.
2. Creates a custom, unique Project ID based on a provided Project Name.
3. Creates the project under the defined Organization node.
4. Grants project ownership to the validated lists of users and/or groups.
5. Links the project to a defined Billing Account.

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
  * [Using the Project Scripts](#using-the-project-scripts)
    * [Modules](#modules)
      * [Cloud Identity Check](#1-cloud-identity-check)
      * [Project ID Creation](#2-project-id-creation)
      * [Project Provisioning](#3-project-provisioning)
      * [Setting IAM Permissions](#4-setting-iam-permissions)
      * [Link Billing Account](#5-link-billing-account)
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
6. A service account must be provisioned in the "Admin" GCP project
7. Access to a valid GCP Billing Account



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


## Using the Project Scripts
### Modules
To aid users in understanding the capabilities of this project, the individual capabilities have been separated and placed in separate scripts. Information on each capability is listed below.

#### 1. Cloud Identity Check
This module iterates through provided lists of users and groups to ensure that they are valid users/groups within the Organization's Cloud Identity.

#### 2. Project ID Creation
This script takes a  project name and lifecycle/environment and creates a corresponding unique project ID which conforms to GCP's naming standards.

#### 3. Project Provisioning
This script provisions the GCP project once it has been confirmed that at least one user or group in the provided lists exists within Cloud Identity.

#### 4. Setting IAM Permissions
This script will grant project ownership to a defined project ID to the provided users and/or groups once the GCP project has been provisioned.

#### 5. Link Billing Account
This script links the newly provisioned GCP project to a defined billing account.


### Using the Main Script
The provision_gcp_project_wrapper.py script calls on the other scripts to provision your GCP project, grant ownership, and link it to a billing account.
#### Variables
The following variables must be set within the provision_gcp_project_wrapper.py file prior to runtime:

* **org_id -** The GCP organization number assigned to your domain. This can be found by navigating to the organization node in the project dropdown.

* **service_account_json_file_path -** This is the file path to the JSON key that corresponds to your Service Account. These scripts have been developed with the assumption that the JSON key is stored on the hosting machine. If you would like to store your keys elsewhere, the Credentials section of the script can be modified. Please see [Google's Authentication page](https://developers.google.com/api-client-library/python/guide/aaa_overview) for further information.

* **admin_email -** This is the email address of a user within your domain that has the ability to view/list users and groups within the Google Admin Console for your organization. Your Service Account acts as this user to verify the user/group information.

* **billing_account_id -** The ID of the billing account that you will link to defined projects.

#### Arguments
The following arguments must be provided when calling the script:

* **project_name -** The name of your GCP project. Must be entered as a string

* **lifecycle -** The project's lifecycle/environment

* **user_list -** A list of user emails that will be checked. The list must encompassed by brackets (e.g., names = [user1@fake.com, user2@fake.com]).

* **group_list -** A list of directory groups that will be checked. The list must be encompassed by brackets (e.g., groups = [group1@fake.com, group2@    fake.com]). The group list is optional.

* **department_code -** The department code that the project belongs to

#### Usage
Once the variables are set, run the script by issuing the following command:

      python provision_gcp_project_wrapper.py "project_name" "lifecycle" "[user_list]"  "[group_list]" "department_code"

#### Expected Output
The completed script will check lists of users and groups, creates a project, tags the project with labels for the lifecylce and department code, grants the users and groups ownership of the project, and links the project to a billing account. Upon successful completion, the script will return a message indicating that the project has been provisioned and will provide the project ID. If no message is returned, please check the logs to see what error has occured.

#### Examples

     python provision_gcp_project_wrapper.py --project_name "My Project" --lifecycle "Dev" --user_list "[user1@fake.com]"  --department_code "123456"
     python provision.py --project_name "eCommerce Site" --lifecycle "Prod" --uesr_list "[user1@fake.com, user2@fake.com]" --grouplist "[group@fake.com]" --department_code "234242"

### Logging
The scripts log various events as they run. The debug.log, info.log, and errors.log files will be generated after the first run of the scripts. Please check these files for information on your script runs.

### Supplementary Scripts
The **add_ons** folder of this project will provide additional scripts to provide functionality that is not included in the primary provision_gcp_project_wrapper.py script. The supplementary scripts allow a user to:
    * Provision a new user in Cloud Identity


#### Provision New User
This script can be used to provision a new user within your Organization's Google Admin Console.

**WARNING:** If the requested user is a conflicting account, the script will     automatically force the user to change the email address associated with th    eir consumer account and does not provide the opportunity to migrate the exi    sting account to your organization. Only use this script for brand new users     or accounts for which you want to reclaim without migrating the associated     data to your organization.
#### Variables
The following variables must be set within the user_provisioning.py file prior to runtime:

* **admin_email -** This is the email address of a user within your domain that has the ability to view/list users and groups within the Google Admin Console for your organization. Your Service Account acts as this user to verify the user/group information.

* **service_account_json_file_path -** This is the file path to the JSON key that corresponds to your Service Account. These scripts have been developed with the assumption that the JSON key is stored on the hosting machine. If you would like to store your keys elsewhere, the Credentials section of the script can be modified. Please see [Google's Authentication page](https://developers.google.com/api-client-library/python/guide/aaa_overview) for further information.

#### Arguments
The following arguments must be provided when calling the script:

* **firstname -** First name of the user that you would like to provision.

* **lastname -** Last name of the user that you would like to provision.

* **email -** Email address of the user that you would like to provision.

* **password -** Optional entry for the password that you would like to provision. If the password is not specified, a random password will be generated.

#### Usage
Once the variables are set, run the script by issuing the following command:

      python user_provisioning.py "firstname" "lastname" "email"  "password"

#### Expected Output
A user will be provisioned in your Organization's Cloud Identity. The script will print a confirmation message once the user is successfully provisioned.

#### Examples
      python user_provisioning.py --firstname "John" --lastname "Doe" --email "johndoe@fake.com"
      python user_provisioning.py --firstname "Jane" --lastname "Doe" --email "janedoe@fake.com" --password "1l1k3appl35"

