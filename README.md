## AWS Resource Manager

AWS Resource Manager is a Python script that provides a menu-driven interface for managing AWS resources, such as S3 buckets and CloudFormation stacks. Users can list, select, and delete resources with ease.

## Features

- List S3 buckets
- Delete S3 bucket by wildcard name
- Delete all S3 buckets
- List CloudFormation stacks
- Delete CloudFormation stack by name
- Delete all CloudFormation stacks

## Prerequisites

Before running the script, make sure you have Python 3.x installed and the latest version of the AWS SDK for Python (Boto3).

To install Boto3, run the following command:

```console
pip install boto3
```

## Configuration

You can provide AWS access key, secret key, and region as command-line arguments. If not provided, the script will use the local computer credentials.

To use local computer credentials, configure your AWS CLI using the following command and follow the prompts:

## Usage

To run the script, navigate to the directory containing the script file and run the following command:

```console
python aws_resource_manager.py
```

To provide AWS access key, secret key, and region as command-line arguments, run the following command:
python aws_resource_manager.py -a YOUR_AWS_ACCESS_KEY -k YOUR_AWS_SECRET_KEY -r YOUR_AWS_REGION

Replace `YOUR_AWS_ACCESS_KEY`, `YOUR_AWS_SECRET_KEY`, and `YOUR_AWS_REGION` with your actual AWS access key, secret key, and region.

## Warning

Deleting resources can be a destructive action. Be cautious when using the delete options, especially when deleting all resources. Always double-check and confirm before proceeding with deletions.

## License

This project is licensed under the MIT License.


