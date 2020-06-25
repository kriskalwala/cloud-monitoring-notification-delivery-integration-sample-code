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

from enum import Enum, unique

import json
import requests


class Error(Exception):
    """Base class for all errors raised in this module."""


class NotificationParseError(Error):
    """Exception raised for errors in a monitoring notification format."""


class UnknownConditionStateError(Error):
    """Exception raised for errors in an invalid incident state value."""


class BadAPIRequestError(Error):
    """Exception raised for errors in a Philips Hue API request."""


class PhilipsHueClient():
    """Client for interacting with different Philips Hue APIs.

    Provides interface to access Philips Hue lights, groups, schedules, etc.

    Attributes:
        bridge_ip_address: IP address of the Hue bridge system to connect to.
        username: Authorized user string to make API calls.
    """
    def __init__(self, bridge_ip_address, username):
        self._bridge_ip_address = bridge_ip_address
        self._username = username


    @property
    def bridge_ip_address(self):
        return self._bridge_ip_address


    @property
    def username(self):
        return self._username


    def set_color(self, light_id, hue):
        """Sets the color of the light to a specified hue value.

        Args:
            light_id:  The id to pass to the Philips Hue API to
                specify the light to set a color for.
            hue: Hue of the light. Takes values from 0 to 65535.
                Programming 0 and 65535 would mean that the light will resemble
                the color red, 25500 for green and 46920 for blue.

        Returns:
            HTTP Response from the Philips Hue API.
        """
        response = requests.put(url=f'http://{self._bridge_ip_address}/api/{self._username}/lights/{light_id}/state',
                                data=json.dumps({"on": True, "hue": hue}))
        if response.status_code != 200:
            raise BadAPIRequestError(response.text)
        return response


# TODO(https://github.com/googleinterns/cloud-monitoring-notification-delivery-integration-sample-code/issues/10):
# Currently specific to Philips Hue, but will be generalized to trigger
# whatever notification system the client chooses.
def trigger_light_from_monitoring_notification(client, notification, light_id, config):
    """Changes the color of a Philips Hue light based on a monitoring notification
    and returns the hue (color) value that the light was set to.

    The color of the Philips Hue light is set through the client,
    which makes an HTTP PUT request to the Philips Hue API.
    Sets the color based off of the name of the policy that
    triggered the notification.

    Args:
        client: The PhilipsHueClient object to trigger a response from.
        notification: A dictionary containing the notification data.
        light_id: The id of the light to set the color for.

    Returns:
        The hue (color) value of the provided Philips Hue after the
        monitoring notification was translated into a light signal,
        and then forwarded to the bulb. A value between 0 and 65535.

    Raises:
        NotificationParseError: If notification is missing required dict key.
        BadAPIRequestError: If there was an error in calling the Philips Hue API.
    """
    try:
        policy_name = notification["incident"]["policy_name"]
    except KeyError:
        raise NotificationParseError("Notification is missing required dict key")

    if policy_name in config["POLICY_HUE_MAPPING"]:
        color = config["POLICY_HUE_MAPPING"][policy_name]
        client.set_color(light_id, color)
        return color
    else:
        color = config["POLICY_HUE_MAPPING"]["default"]
        client.set_color(light_id, color)
        return color
