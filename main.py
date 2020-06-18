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

# The code in this module is based on https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/run/pubsub/main.py. 
# See https://cloud.google.com/run/docs/tutorials/pubsub for the accompanying Cloud Run/PubSub solutions guide.

# [START run_pubsub_server_setup]
import base64
import binascii
import os
import json
import philips_hue

from flask import Flask, request
from config import configs
import google_monitoring

from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
env = os.environ.get('FLASK_APP_ENV', 'default')
app.config.from_object(configs[env])
# [END run_pubsub_server_setup]

        
# [START run_pubsub_handler]
@app.route('/', methods=['POST'])
def index():
    pubsub_envelope = request.get_json()
    
    # parse the Pub/Sub notification
    try:
        notification_dict = google_monitoring.parse_notification_from_pubsub_envelope(pubsub_envelope)
    except google_monitoring.NotificationParseError as e:
        print(e)
        return (e.message, 400)
    
    # parse the incident from the notification
    try:
        incident = google_monitoring.parse_incident_from_notification(notification_dict)
        print(incident)
    except google_monitoring.IncidentParseError as e:
        print(e)
        return (e.message, 400)

    philips_hue_client = philips_hue.PhilipsHueClient(app.config['BRIDGE_IP_ADDRESS'], app.config['USERNAME'])
    
    try:
        response = philips_hue.trigger_hue_from_incident(philips_hue_client, incident, app.config['LIGHT_ID'])  
    except ValueError as e:
        print(e)
        return (e.message, 400)


    return (response.text, 200)
# [END run_pubsub_handler]


if __name__ == '__main__':
    PORT = int(os.getenv('PORT')) if os.getenv('PORT') else 8080

    # This is used when running locally. Gunicorn is used to run the
    # application on Cloud Run. See entrypoint in Dockerfile.
    app.run(host='127.0.0.1', port=PORT, debug=True)
