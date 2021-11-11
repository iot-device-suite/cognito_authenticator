import boto3
import os

ACCOUNT_ID = os.environ.get("ACCOUNT_ID", "012845820164")
AWS_REGION = os.environ.get("AWS_REGION", "eu-central-1")
CLIENT_ID = os.environ.get("CLIENT_ID", "58cn4ra5bg54m30jnklhludn9n")
IDENTITY_POOL_ID = os.environ.get("IDENTITY_POOL_ID", "eu-central-1:51e7519b-4b3b-4723-b356-7bec0273316d")
USER_POOL_PROVIDER_ID = os.environ.get("USER_POOL_PROVIDER_ID", "eu-central-1_u3YeXoQtL")

# Create the Cognito Identity Provider Handler
cognito_idp_client = boto3.client("cognito-idp")

# Create the Cognito Identity Handler
cognito_identity_client = boto3.client("cognito-identity")

# Ask the User for his User Name and Password
print("Please enter your User Name:")
user_name = input()
print("Please enter your Password:")
password = input()
print("Please input TOTP:")
totp_value = input()

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

response = cognito_idp_client.respond_to_auth_challenge(
    ClientId=CLIENT_ID,
    ChallengeName="SOFTWARE_TOKEN_MFA",
    Session=response.get("Session"),
    ChallengeResponses={
        "USERNAME": auth_parameters.get("USERNAME"),
        "SOFTWARE_TOKEN_MFA_CODE": totp_value
    }
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

