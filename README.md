# dashboard_update
Script to update SPARC dataset dashboard. The script will iterate over all SPARC datasets and update records in the "SPARC Datasets" dataset accordingly.

## Setup
This script can run locally, or be deployed as a recurring lambda function on AWS.

### Locally
Use setuptools to build the script locally. Then, call `sparc_dash update` from the command-line. You will need to have the Blackfynn Python client installed and configured your api keys.

In addition, you will need to specify the following environment variables:

`SCICRUNCH_API_KEY=xxxxxxxxxxxxxxxxxxxxx`

### AWS
You will need to install the AWS command line tools and setup your amazon account in your console such that the CLI has access to the AWS Account where the script will run.

You will need to package the script and dependencies into a ZIP file and upload to an accessible S3 location. The `build_lambda.sh` shell script does that for you. Before running this shell-script, update the version of the lambda in the `build_lambda.sh` file. Once this script has run, a zipped file with all requirements for the lambda function is stored on S3.

Next, you can build the required AWS infrastructure to run the script periodically using Terraform. In order to set this up on an AWS account, you will need to create terrraform file that contains environment variables (and not commit this to Github!).

This file needs to be called 'terraform.tfvars', be located in the `Terraform` folder and contain the following content:

```
bf_token = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxx"
bf_secret = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxx"
aws_account = "xxxxx"
dataset_name = "SPARC_Datasets"
bucket = "{bucket-name location lambda zip}"
scicrunch_api_key = "xxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

To build the infrastructure, run:

`terraform apply` 

in the Terraform folder. After running the Terraform scripts, make sure you check the AWS account as setting up infrastructure on AWS can result in incurred costs (although very minimal in this case)