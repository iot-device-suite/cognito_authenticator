import boto3
import os
import getpass

from environs import Env

env = Env()
env.read_env()

ACCOUNT_ID = env("ACCOUNT_ID")
CLIENT_ID = env("CLIENT_ID")
IDENTITY_POOL_ID = env("IDENTITY_POOL_ID")
USER_POOL_PROVIDER_ID = env("USER_POOL_PROVIDER_ID")
AWS_REGION = env("AWS_REGION")


# Create the Cognito Identity Provider Handler
cognito_idp_client = boto3.client("cognito-idp")

# Create the Cognito Identity Handler
cognito_identity_client = boto3.client("cognito-identity")

# Ask the User for his User Name and Password
print("User Name:")
user_name = input()
password = getpass.getpass()

auth_parameters = {
    "USERNAME": user_name,
    "PASSWORD": password
}

# Get the ID Token
response = cognito_idp_client.initiate_auth(
    AuthFlow="USER_PASSWORD_AUTH",
    AuthParameters=auth_parameters,
    ClientId=CLIENT_ID
)

id_token = response["AuthenticationResult"]["IdToken"]

# Create Cognito URL
cognito_url = "cognito-idp." + AWS_REGION + ".amazonaws.com/" + USER_POOL_PROVIDER_ID

# Get the Identity ID
response = cognito_identity_client.get_id(
    AccountId=ACCOUNT_ID,
    IdentityPoolId=IDENTITY_POOL_ID,
    Logins={
        cognito_url: id_token
    }
)

identity_id = response["IdentityId"]

# Get Credentitals for the Identity
response = cognito_identity_client.get_credentials_for_identity(
    IdentityId=identity_id,
    Logins={
        cognito_url: id_token
    }
)

# Get the Credentials from the Response and set the Environment Variables
user_access_key_id = response["Credentials"]["AccessKeyId"]
user_secret_access_key = response["Credentials"]["SecretKey"]
session_token = response["Credentials"]["SessionToken"]

# os.environ["user_access_key_id"] = user_access_key_id
# os.environ["user_secret_access_key"] = user_secret_access_key
# os.environ["session_token"] = session_token

print("ACCESS_KEY_ID:")
print(user_access_key_id)
print("SECRET_ACCESS_KEY:")
print(user_secret_access_key)
print("SESSION_TOKEN")
print(session_token)
