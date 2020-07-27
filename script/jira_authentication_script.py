import requests
from oauthlib.oauth1 import SIGNATURE_RSA
from requests_oauthlib import OAuth1Session
from jira.client import JIRA
from Crypto.PublicKey import RSA
from google.cloud import secretmanager
from google.api_core.exceptions import AlreadyExists

def read(file_path):
    """ Read a file and return it's contents. """
    with open(file_path) as f:
        return f.read()

def create_secret(client, project_id, secret_id):
    """
    Create a new secret with the given name. A secret is a logical wrapper
    around a collection of secret versions. Secret versions hold the actual
    secret material.
    """

    # Build the resource name of the parent project.
    parent = client.project_path(project_id)

    # Create the secret.
    response = client.create_secret(parent, secret_id, {
        'replication': {
            'automatic': {},
        },
    })

    # Print the new secret name.
    print('Created secret: {}'.format(response.name))


def add_secret_version(client, project_id, secret_id, payload):
    """
    Add a new secret version to the given secret with the provided payload.
    """
    
    # Build the resource name of the parent secret.
    parent = client.secret_path(project_id, secret_id)

    # Convert the string payload into a bytes. This step can be omitted if you
    # pass in bytes instead of a str for the payload argument.
    payload = payload.encode('UTF-8')

    # Add the secret version.
    response = client.add_secret_version(parent, {'data': payload})

    # Print the new secret version name.
    print('Added secret version: {}'.format(response.name))


private_key = RSA.generate(2048)
private_key_pem = private_key.exportKey('PEM')
with open("private.pem", "wb") as f:
    f.write(private_key_pem)

public_key = private_key.publickey()
public_key_pem = public_key.exportKey('PEM')
with open("public.pem", "wb") as f:
    f.write(public_key_pem)

while input("Press any key to continue..."):
    pass

# The Consumer Key created while setting up the "Incoming Authentication" in
# JIRA for the Application Link.
CONSUMER_KEY = 'OauthKey'

# The contents of the rsa.pem file generated (the private RSA key)
RSA_KEY = private_key_pem

# The URLs for the JIRA instance
JIRA_SERVER = 'http://localhost:8080'
REQUEST_TOKEN_URL = JIRA_SERVER + '/plugins/servlet/oauth/request-token'
AUTHORIZE_URL = JIRA_SERVER + '/plugins/servlet/oauth/authorize'
ACCESS_TOKEN_URL = JIRA_SERVER + '/plugins/servlet/oauth/access-token'


# Step 1: Get a request token

oauth = OAuth1Session(CONSUMER_KEY, signature_type='auth_header',
                      signature_method=SIGNATURE_RSA, rsa_key=RSA_KEY,
                      verifier="jira_verifier")
request_token = oauth.fetch_request_token(REQUEST_TOKEN_URL)

print("STEP 1: GET REQUEST TOKEN")
print("  oauth_token={}".format(request_token['oauth_token']))
print("  oauth_token_secret={}".format(request_token['oauth_token_secret']))
print("\n")


# Step 2: Get the end-user's authorization

print("STEP2: AUTHORIZATION")
print("  Visit to the following URL to provide authorization:")
print("  {}?oauth_token={}".format(AUTHORIZE_URL, request_token['oauth_token']))
print("\n")

while input("Press any key to continue..."):
    pass


# Step 3: Get the access token

access_token = oauth.fetch_access_token(ACCESS_TOKEN_URL)
oauth_token = access_token['oauth_token']
oauth_token_secret = access_token['oauth_token_secret']

print("STEP2: GET ACCESS TOKEN")
print("  oauth_token={}".format(oauth_token))
print("  oauth_token_secret={}".format(oauth_token_secret))
print("\n")


# SECRET MANAGER

project_id = "alertmanager-2020-intern-r"

client = secretmanager.SecretManagerServiceClient()

try:
    create_secret(client, project_id, "jira_access_token")
except AlreadyExists as e:
    print('Secret already exists: "jira_access_token"')

try:
    create_secret(client, project_id, "jira_access_token_secret")
except AlreadyExists as e:
    print('Secret already exists: "jira_access_token_secret"')

try:
    create_secret(client, project_id, "jira_consumer_key")
except AlreadyExists as e:
    print('Secret already exists: "jira_consumer_key"')

try:
    create_secret(client, project_id, "jira_cert_key")
except AlreadyExists as e:
    print('Secret already exists: "jira_cert_key"')


add_secret_version(client, project_id, "jira_access_token", oauth_token)
add_secret_version(client, project_id, "jira_access_token_secret", oauth_token_secret)
add_secret_version(client, project_id, "jira_consumer_key", CONSUMER_KEY)
add_secret_version(client, project_id, "jira_cert_key", private_key_pem)




# Now you can use the access tokens with the JIRA client. Hooray!

jira = JIRA(options={'server': JIRA_SERVER}, oauth={
    'access_token': access_token['oauth_token'],
    'access_token_secret': access_token['oauth_token_secret'],
    'consumer_key': CONSUMER_KEY,
    'key_cert': RSA_KEY
})

# print all of the project keys just as an exmaple
for project in jira.projects():
    print(project.key)