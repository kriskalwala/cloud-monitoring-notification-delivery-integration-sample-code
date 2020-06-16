# Copyright 2019 Google, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# The code in this module is based on https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/run/pubsub/main.py. See https://cloud.google.com/run/docs/tutorials/pubsub for the accompanying Cloud Run/PubSub solutions guide.

# [START run_pubsub_server_setup]
import base64
import binascii
import os
import json
import philips_hue

from flask import Flask, request
from config import configs

from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
env = os.environ.get('FLASK_APP_ENV', 'default')
app.config.from_object(configs[env])

philips_hue_client = philips_hue.PhilipsHueClient(app.config['PHILIPS_HUE_URL'])
# [END run_pubsub_server_setup]


# TODO(https://github.com/googleinterns/cloud-monitoring-notification-delivery-integration-sample-code/issues/10): 
# Currently specific to Philips Hue, but will be generalized to trigger whatever notification system the client chooses
def trigger_hue_from_incident(client, incident, light_id):
    """Changes the color of a Philips Hue light based on an incident message from pub/sub and returns the response.
    
    Sets the color of the light to red if the incident is open and green if the incident is closed.

    Args:
        incident: A JSON message about an incident from pub/sub.
        light_id: The id of the light to set the color for.
    
    Returns:
        The HTTP Response from calling the Philips Hue API.
    """
    condition_state = incident["incident"]["condition"]["state"]
    if condition_state == "open":
        return client.set_color(light_id, 0)  # set to red
    elif condition_state == "closed":
        return client.set_color(light_id, 25500)  # set to green
        

# TODO(https://github.com/googleinterns/cloud-monitoring-notification-delivery-integration-sample-code/issues/11): 
# Currently using if statements to check if certain keys exist, but will potentially use the jsonschema library
# in the future to validate messages
def is_valid_pubsub_message(envelope):
    """Returns whether or not a JSON envelope has the correct pubsub message schema.

    Args:
        envelope: The JSON response to validate.
        
    Returns:
        True if the envelope has a valid message format, False otherwise.
    """
    if not isinstance(envelope, dict) or 'message' not in envelope:
        return False

    pubsub_message = envelope['message']

    if not isinstance(pubsub_message, dict) or 'data' not in pubsub_message:
        return False
    
    return True

# TODO(https://github.com/googleinterns/cloud-monitoring-notification-delivery-integration-sample-code/issues/11): 
# Currently using if statements to check if certain keys exist, but will potentially use the jsonschema library
# in the future to validate messages
def is_valid_incident_message(message):
    """Returns whether or not a message has the correct incident message schema.

    Args:
        message: The JSON notification to validate.
        
    Returns:
        True if the message has a valid incident format, False otherwise.
    """
    if not isinstance(message, dict) or 'incident' not in message:
        return False
    
    return True

        
# [START run_pubsub_handler]
@app.route('/', methods=['POST'])
def index():
    envelope = request.get_json()
    
    if not envelope:
        msg = 'no Pub/Sub message received'
        print(f'error: {msg}')
        return f'Bad Request: {msg}', 400

    if not is_valid_pubsub_message(envelope):
        msg = 'invalid Pub/Sub message format'
        print(f'error: {msg}')
        return f'Bad Request: {msg}', 400
    
    pubsub_message = envelope['message']
    
    
    try:
        monitoring_notification_string = base64.b64decode(pubsub_message['data']).decode('utf-8').strip()
    except (TypeError, binascii.Error) as e:
        msg = 'notification should be base64-encoded'
        print(f'error: {msg}')
        return f'Bad Request: {msg}', 400
    
    
    try:
        monitoring_notification_dict = json.loads(monitoring_notification_string)
    except json.JSONDecodeError:
        msg = 'notification could not be decoded to a JSON'
        print(f'error: {msg}')
        return f'Bad Request: {msg}', 400
    
     
    if not is_valid_incident_message(monitoring_notification_dict):
        msg = 'invalid incident format'
        print(f'error: {msg}')
        return f'Bad Request: {msg}', 400

    
    r = trigger_hue_from_incident(philips_hue_client, monitoring_notification_dict, app.config['LIGHT_ID'])  


    return (r.text, 200)
# [END run_pubsub_handler]


if __name__ == '__main__':
    PORT = int(os.getenv('PORT')) if os.getenv('PORT') else 8080

    # This is used when running locally. Gunicorn is used to run the
    # application on Cloud Run. See entrypoint in Dockerfile.
    app.run(host='127.0.0.1', port=PORT, debug=True)