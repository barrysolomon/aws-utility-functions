import argparse
import boto3
import time
import fnmatch
from botocore.exceptions import ClientError

def parse_arguments():
    parser = argparse.ArgumentParser(description='Manage AWS resources: S3 buckets and CloudFormation stacks.')
    parser.add_argument('-a', '--aws_access_key', required=False, help='Your AWS access key. If not provided, local computer credentials will be used.')
    parser.add_argument('-k', '--aws_secret_key', required=False, help='Your AWS secret key. If not provided, local computer credentials will be used.')
    parser.add_argument('-r', '--aws_region', default='us-west-2', help='The AWS region where the resources are located (default: us-west-2).')
    return parser.parse_args()

def create_session(aws_access_key, aws_secret_key, aws_region):
    if aws_access_key and aws_secret_key:
        session = boto3.Session(aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=aws_region)
    else:
        session = boto3.Session(region_name=aws_region)
    return session

def list_s3_buckets(s3_client):
    response = s3_client.list_buckets()
    return [bucket['Name'] for bucket in response['Buckets']]

def list_cloudformation_stacks(cf_client):
    response = cf_client.list_stacks(StackStatusFilter=['CREATE_COMPLETE', 'ROLLBACK_COMPLETE', 'UPDATE_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE'])
    return [stack['StackName'] for stack in response['StackSummaries']]

def delete_s3_bucket(s3_client, bucket_name):
    # Empty the bucket first
    paginator = s3_client.get_paginator('list_object_versions')
    for page in paginator.paginate(Bucket=bucket_name):
        for version in page.get('Versions', []):
            s3_client.delete_object(Bucket=bucket_name, Key=version['Key'], VersionId=version['VersionId'])
        for marker in page.get('DeleteMarkers', []):
            s3_client.delete_object(Bucket=bucket_name, Key=marker['Key'], VersionId=marker['VersionId'])
    # Delete the bucket
    s3_client.delete_bucket(Bucket=bucket_name)

def delete_cloudformation_stack(cf_client, stack_name):
    cf_client.delete_stack(StackName=stack_name)

    # Wait for stack deletion
    print(f"Waiting for stack '{stack_name}' to be deleted...")
    while True:
        try:
            stack_status = cf_client.describe_stacks(StackName=stack_name)['Stacks'][0]['StackStatus']
            if stack_status == 'DELETE_IN_PROGRESS':
                time.sleep(10)
            elif stack_status == 'DELETE_FAILED':
                print(f"Stack deletion failed for '{stack_name}'. Please delete manually.")
                break
            elif stack_status == 'DELETE_COMPLETE':
                print(f"Stack '{stack_name}' has been successfully deleted.")
                break
        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationError' and 'does not exist' in str(e):
                print(f"Warning: Stack '{stack_name}' not found.")
                break
            else:
                raise e

def menu(options):
    print("\nPlease choose an option:")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    choice = int(input("\nEnter the number of your choice: "))
    return options[choice - 1]

def main():
    args = parse_arguments()
    aws_access_key = args.aws_access_key
    aws_secret_key = args.aws_secret_key
    aws_region = args.aws_region

    session = create_session(aws_access_key, aws_secret_key, aws_region)

    s3_client = session.client('s3')
    cf_client = session.client('cloudformation')

    while True:
        resource_type = menu(["S3 Bucket", "CloudFormation Stack", "Exit"])

        if resource_type == "S3 Bucket":
            action = menu(["List S3 Buckets", "Delete S3 Bucket by Wildcard Name", "Delete All S3 Buckets", "Go Back"])

            if action == "List S3 Buckets":
                s3_buckets = list_s3_buckets(s3_client)
                print("\nS3 Buckets:")
                for bucket in s3_buckets:
                    print(bucket)

            elif action == "Delete S3 Bucket by Wildcard Name":
                bucket_wildcard = input("\nEnter the wildcard for matching S3 bucket names: ")

                matching_buckets = [bucket for bucket in list_s3_buckets(s3_client) if fnmatch.fnmatch(bucket, bucket_wildcard)]

                if not matching_buckets:
                    print(f"No buckets matching the wildcard '{bucket_wildcard}' found.")
                else:
                    print("\nMatching S3 Buckets:")
                    for bucket in matching_buckets:
                        print(bucket)

                    confirm = input("\nAre you sure you want to delete these buckets? (y/n) ")
                    if confirm.lower() == "y":
                        for bucket in matching_buckets:
                            print(f"Deleting bucket: {bucket}")
                            delete_s3_bucket(s3_client, bucket)

            elif action == "Delete All S3 Buckets":
                all_buckets = list_s3_buckets(s3_client)

                if not all_buckets:
                    print("No S3 buckets found.")
                else:
                    print("\nAll S3 Buckets:")
                    for bucket in all_buckets:
                        print(bucket)

                    confirm = input("\nAre you sure you want to delete all S3 buckets? (y/n) ")
                    if confirm.lower() == "y":
                        for bucket in all_buckets:
                            print(f"Deleting bucket: {bucket}")
                            delete_s3_bucket(s3_client, bucket)

        elif resource_type == "CloudFormation Stack":
            action = menu(["List CloudFormation Stacks", "Delete CloudFormation Stack by Name", "Delete All CloudFormation Stacks", "Go Back"])

            if action == "List CloudFormation Stacks":
                stacks = list_cloudformation_stacks(cf_client)
                print("\nCloudFormation Stacks:")
                for stack in stacks:
                    print(stack)

            elif action == "Delete CloudFormation Stack by Name":
                stack_name = input("\nEnter the name of the CloudFormation stack to be deleted: ")

                if stack_name not in list_cloudformation_stacks(cf_client):
                    print(f"Warning: Stack '{stack_name}' not found.")
                else:
                    confirm = input("\nAre you sure you want to delete this stack? (y/n) ")
                    if confirm.lower() == "y":
                        print(f"Deleting CloudFormation stack '{stack_name}'...")
                        delete_cloudformation_stack(cf_client, stack_name)

            elif action == "Delete All CloudFormation Stacks":
                all_stacks = list_cloudformation_stacks(cf_client)

                if not all_stacks:
                    print("No CloudFormation stacks found.")
                else:
                    print("\nAll CloudFormation Stacks:")
                    for stack in all_stacks:
                        print(stack)

                    confirm = input("\nAre you sure you want to delete all CloudFormation stacks? (y/n) ")
                    if confirm.lower() == "y":
                        for stack in all_stacks:
                            print(f"Deleting CloudFormation stack '{stack}'...")
                            delete_cloudformation_stack(cf_client, stack)

        elif resource_type == "Exit":
            print("Exiting...")
            break

if __name__ == '__main__':
    main()
