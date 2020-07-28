import argparse
from requests_oauthlib import OAuth1Session
from oauthlib.oauth1 import SIGNATURE_RSA
from Crypto.PublicKey import RSA
from google.cloud import secretmanager
from google.api_core.exceptions import AlreadyExists


def create_secret(client, project_id, secret_id):
    """
    Create a new secret with the given name. A secret is a logical wrapper
    around a collection of secret versions. Secret versions hold the actual
    secret material.
    """

    parent = client.project_path(project_id)
    response = client.create_secret(parent, secret_id, {
        'replication': {
            'automatic': {},
        },
    })
    print('Created secret: {}'.format(response.name))


def add_secret_version(client, project_id, secret_id, payload):
    """
    Add a new secret version to the given secret with the provided payload.
    """
    
    parent = client.secret_path(project_id, secret_id)

    if not isinstance(payload, bytes):
        payload = payload.encode('UTF-8')

    response = client.add_secret_version(parent, {'data': payload})
    print('Added secret version: {}'.format(response.name))


parser = argparse.ArgumentParser(description=('Setup Jira Server OAuth'))

parser.add_argument('project_id',
                    help='id of Google Cloud project to store secrets in')

parser.add_argument('jira_url',
                    help='URL of the Jira Server to setup OAuth for')

parser.add_argument('-m',
                    action='store_true',
                    help='use already generated private/public RSA keys called private.pem and public.pem')

args = parser.parse_args()


# Create or read in RSA public and private keys
if args.m:
    with open('private.pem') as f:
        private_key_pem = f.read()

    with open('public.pem') as f:
        public_key_pem = f.read()

    print("RSA public and private keys loaded")
else:
    private_key = RSA.generate(2048)
    private_key_pem = private_key.exportKey('PEM')
    with open('private.pem', 'wb') as f:
        f.write(private_key_pem)

    public_key = private_key.publickey()
    public_key_pem = public_key.exportKey('PEM')
    with open('public.pem', 'wb') as f:
        f.write(public_key_pem)

    print("RSA public and private keys created")



# Setup Jira Oauth
consumer_key = 'CloudMonitoringOauthKey'

print(f"""\nComplete the following steps:
1. In Jira, navigate to Jira Settings > Applications > Application Links
2. In the 'Enter the URL of the application you want to link' field, enter http://example.com/
3. On the first screen of the 'Link applications' dialog, select the 'Create incoming link' checkbox and click 'Continue'
4. On next screen of the 'Link applications' dialog, enter the following consumer details:
    * Consumer Key: {consumer_key}
    * Consumer Name: Cloud Monitoring App
    * Public Key:\n{public_key_pem}
5: Click 'Continue'

(Note the previous steps are based off of the instructions at https://developer.atlassian.com/server/jira/platform/oauth/#create-an-application-link)\n""")

input('Once complete, press "Enter" to proceed\n')

oauth = OAuth1Session(consumer_key,
                      signature_method=SIGNATURE_RSA,
                      rsa_key=private_key_pem,
                      signature_type='auth_header',
                      verifier='jira_verifier')

request_token_url = f'{args.jira_url}/plugins/servlet/oauth/request-token'
fetch_response = oauth.fetch_request_token(request_token_url)
oauth_token = fetch_response.get('oauth_token')
oauth_token_secret = fetch_response.get('oauth_token_secret')

base_authorization_url =  f'{args.jira_url}/plugins/servlet/oauth/authorize'
authorization_url = oauth.authorization_url(base_authorization_url)
print(f'Go to the following URL and click allow: {authorization_url}\n')
input('Once complete, press "Enter" to proceed\n')

access_token_url = f'{args.jira_url}/plugins/servlet/oauth/access-token'
oauth_tokens = oauth.fetch_access_token(access_token_url)
oauth_token = oauth_tokens.get('oauth_token')
oauth_token_secret = oauth_tokens.get('oauth_token_secret')

with open('jira_access_token.txt', 'w') as f:
        f.write(oauth_token)
print('Jira access token stored in jira_access_token.txt')

with open('jira_access_token_secret.txt', 'w') as f:
        f.write(oauth_token_secret)
print('Jira access token secret stored in jira_access_token_secret.txt')



# Store Oauth data necessary to authenticate Jira in Google Secret Manager
client = secretmanager.SecretManagerServiceClient()

try:
    create_secret(client, project_id, 'jira_access_token')
except AlreadyExists as e:
    print('Secret already exists: "jira_access_token"')

try:
    create_secret(client, project_id, 'jira_access_token_secret')
except AlreadyExists as e:
    print('Secret already exists: "jira_access_token_secret"')

try:
    create_secret(client, project_id, 'jira_consumer_key')
except AlreadyExists as e:
    print('Secret already exists: "jira_consumer_key"')

try:
    create_secret(client, project_id, 'jira_key_cert')
except AlreadyExists as e:
    print('Secret already exists: "jira_key_cert"')


add_secret_version(client, project_id, 'jira_access_token', oauth_token)
add_secret_version(client, project_id, 'jira_access_token_secret', oauth_token_secret)
add_secret_version(client, project_id, 'jira_consumer_key', consumer_key)
add_secret_version(client, project_id, 'jira_key_cert', private_key_pem)

print("Successfully setup Jira Authentication!")
