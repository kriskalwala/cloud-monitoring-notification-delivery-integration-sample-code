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

# The code in this module is based on
# https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/run/pubsub/main.py.
# See https://cloud.google.com/run/docs/tutorials/pubsub for the accompanying
# Cloud Run/PubSub solutions guide.

"""Runs Cloud Monitoring Notification Integration app with Flask."""

# [START run_pubsub_server_setup]
import os
import json

from flask import Flask, request

import philips_hue
import config
import pubsub


app = Flask(__name__)
app.config.from_object(config.load())
# [END run_pubsub_server_setup]


# [START run_pubsub_handler]
@app.route('/', methods=['POST'])
def handle_pubsub_message():
    pubsub_received_message = request.get_json()

    # parse the Pub/Sub data
    try:
        pubsub_data_string = pubsub.parse_data_from_message(pubsub_received_message)
    except pubsub.DataParseError as e:
        print(e)
        return (str(e), 400)

    # load the notification from the data
    try:
        monitoring_notification_dict = json.loads(pubsub_data_string)
    except json.JSONDecodeError as e:
        print(e)
        return (f'Notification could not be decoded due to the following exception: {e}', 400)


    philips_hue_client = philips_hue.PhilipsHueClient(app.config['BRIDGE_IP_ADDRESS'],
                                                      app.config['USERNAME'])

    try:
        hue_state = philips_hue.trigger_light_from_monitoring_notification(
            philips_hue_client, monitoring_notification_dict,
            app.config['LIGHT_ID'], app.config)
    except philips_hue.Error as e:
        print(e)
        return (str(e), 400)


    return (repr(hue_state), 200)
# [END run_pubsub_handler]


if __name__ == '__main__':
    PORT = int(os.getenv('PORT')) if os.getenv('PORT') else 8080

    # This is used when running locally. Gunicorn is used to run the
    # application on Cloud Run. See entrypoint in Dockerfile.
    app.run(host='127.0.0.1', port=PORT, debug=True)
