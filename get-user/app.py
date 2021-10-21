import json
import boto3

def lambda_handler(event, context):
    sts_connection = boto3.client('sts')
    assRole = sts_connection.assume_role(
        RoleArn="arn:aws:iam::${aws-account}:role/userAssumeRole",
        RoleSessionName="userAssumeRoleSession",
        Policy="{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"dynamodb:GetItem\",\"dynamodb:BatchGetItem\",\"dynamodb:Query\"],\"Resource\":[\"arn:aws:dynamodb:ap-northeast-1:${aws-account}:table/Sample\"],\"Condition\":{\"ForAllValues:StringEquals\":{\"dynamodb:LeadingKeys\":[\"User1\"]}}}]}",
    )
    ACCESS_KEY = assRole['Credentials']['AccessKeyId']
    SECRET_KEY = assRole['Credentials']['SecretAccessKey']
    SESSION_TOKEN = assRole['Credentials']['SessionToken']
    client = boto3.client(
        'dynamodb',
         aws_access_key_id = ACCESS_KEY,
         aws_secret_access_key = SECRET_KEY,
         aws_session_token = SESSION_TOKEN
    )
    response = client.get_item(
        TableName="Sample",
        Key={
            'id': {
                "S": "User1"
            }
        }
    )
    print(response)
    return "OK"