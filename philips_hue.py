# Copyright 2020 Google, LLC.
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

# Philips Hue API Documentation: https://developers.meethue.com/develop/hue-api/

"""Module to handle interactions with a Philips Hue system.

This module defines Philips Hue classes, as well as
callback functions that interact with a Philips Hue client.
"""

import json
import requests


class PhilipsHueClient():
    """Client for interacting with different Philips Hue APIs.

    Provides interface to access Philips Hue lights, groups, schedules, etc.

    Attributes:
        bridge_ip_address: IP address of the Hue bridge system to connect to.
        username: Authorized user string to make API calls.
    """
    def __init__(self, bridge_ip_address, username):
        self.bridge_ip_address = bridge_ip_address
        self.username = username


    def set_color(self, light_id, hue):
        """Sets the color of the light to a specified hue value.

        Args:
            light_id:  The id to pass to the Philips Hue API to
                specify the light to set a color for.
            hue: Hue of the light. Takes values from 0 to 65535.
                Programming 0 and 65535 would mean that the light will resemble
                the color red, 21845 for green and 43690 for blue.

        Returns:
            HTTP Response from the Philips Hue API.
        """
        return requests.put(url=f'http://{self.bridge_ip_address}/api/{self.username}/lights/{light_id}/state',
                            data=json.dumps({"on": True, "hue": hue}))


class Error(Exception):
    """Base class for exceptions in this module.

    Attributes:
        message: explanation of the error
    """
    def __init__(self, message):
        self.message = message


class NotificationParseError(Error):
    """Exception raised for errors in a monitoring notification format."""
    pass


class StateValueError(Error):
    """Exception raised for errors in an invalid incident state value."""
    pass


# TODO(https://github.com/googleinterns/cloud-monitoring-notification-delivery-integration-sample-code/issues/10):
# Currently specific to Philips Hue, but will be generalized to trigger
# whatever notification system the client chooses.
def trigger_light_from_monitoring_notification(client, notification, light_id):
    """Changes the color of a Philips Hue light based on a monitoring notification
    and returns the response.

    Sets the color of the light to red if the incident is open and green if the incident is closed.

    Args:
        client: The PhilipsHueClient object to trigger a response from.
        notification: A JSON message about a monitoring notification.
        light_id: The id of the light to set the color for.

    Returns:
        The HTTP Response from calling the Philips Hue API.

    Raises:
        ValueError: If the incident state is not open or closed.
    """
    try:
        condition_state = notification["incident"]["condition"]["state"]
    except KeyError:
        raise NotificationParseError("invalid incident format")

    if condition_state == "open":
        return client.set_color(light_id, 0)  # set to red
    if condition_state == "closed":
        return client.set_color(light_id, 25500)  # set to green

    raise StateValueError("incident state should be either open or closed")
