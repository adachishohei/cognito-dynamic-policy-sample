import json
import boto3
import time
import urllib.request
from jose import jwk, jwt
from jose.utils import base64url_decode

region = "ap-northeast-1"
userpool_id = "ap-northeast-1_UlEqYl7Ou"
app_client_id = "3da26qrsnsv5hn697j1h2et0j1"
keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(region, userpool_id)

with urllib.request.urlopen(keys_url) as f:
    response = f.read()
keys = json.loads(response.decode('utf-8'))['keys']


def lambda_handler(event, context):
    print(event)
    token = event['headers']['Authorization']
    print(token)
    claim = decode_token(token)
    policy = get_policy(claim["cognito:username"])
    sts_connection = boto3.client('sts')
    assRole = sts_connection.assume_role(
        RoleArn="arn:aws:iam::261812635110:role/userAssumeRole",
        RoleSessionName="userAssumeRoleSession",
        Policy=policy
    )
    ACCESS_KEY = assRole['Credentials']['AccessKeyId']
    SECRET_KEY = assRole['Credentials']['SecretAccessKey']
    SESSION_TOKEN = assRole['Credentials']['SessionToken']
    client = boto3.client(
        'dynamodb',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        aws_session_token=SESSION_TOKEN
    )
    response = client.get_item(
        TableName="Sample",
        Key={
            'id': {
                "S": claim["cognito:username"]
            }
        }
    )
    print(response)
    return {
        "statusCode": 200,
        "body": "OK",
    }


def get_policy(leading_key):
    print(leading_key)
    return "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"dynamodb:GetItem\",\"dynamodb:BatchGetItem\",\"dynamodb:Query\"],\"Resource\":[\"arn:aws:dynamodb:ap-northeast-1:261812635110:table/Sample\"],\"Condition\":{\"ForAllValues:StringEquals\":{\"dynamodb:LeadingKeys\":[\"" + leading_key + "\"]}}}]}"

def decode_token(token):
    headers = jwt.get_unverified_headers(token)
    kid = headers['kid']
    key_index = -1
    for i in range(len(keys)):
        if kid == keys[i]['kid']:
            key_index = i
            break
    if key_index == -1:
        print('Public key not found in jwks.json')
        return False

    public_key = jwk.construct(keys[key_index])
    message, encoded_signature = str(token).rsplit('.', 1)
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    if not public_key.verify(message.encode("utf8"), decoded_signature):
        print('Signature verification failed')
        return False
    print('Signature successfully verified')
    claims = jwt.get_unverified_claims(token)
    if time.time() > claims['exp']:
        print('Token is expired')
        return False
    # and the Audience  (use claims['client_id'] if verifying an access token)
    if claims['aud'] != app_client_id:
        print('Token was not issued for this audience')
        return False
    # now we can use the claims
    print(claims)
    return claims
