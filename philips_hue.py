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


class UnknownIncidentStateError(Error):
    """Exception raised for errors in an invalid incident state value."""


class BadAPIRequestError(Error):
    """Exception raised for errors in a Philips Hue API request."""


@unique
class PhilipsHueState(Enum):
    """Enum mapping an incident state to hue of Philips Hue bulb."""
    OPEN = 0
    CLOSED = 25500


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
def trigger_light_from_monitoring_notification(client, notification, light_id):
    """Changes the color of a Philips Hue light based on a monitoring notification
    and returns the response.

    The color of the Philips Hue light is set through the client,
    which makes an HTTP PUT request to the Philips Hue API.
    Sets the color of the light to red if the incident is open and green if the incident is closed.

    Args:
        client: The PhilipsHueClient object to trigger a response from.
        notification: A dictionary containing the notification data.
        light_id: The id of the light to set the color for.

    Returns:
        The state of the provided Philips Hue after the monitoring notification
        was translated into a light signal, and then forwarded to the bulb.
        One of PhilipsHueState.

    Raises:
        UnknownIncidentStateError: If the incident state is not open or closed.
        BadAPIRequestError: If there was an error in calling the Philips Hue API.
    """
    try:
        incident_state = notification["incident"]["state"]
    except KeyError:
        raise NotificationParseError("Notification is missing required dict key")

    if incident_state == "open":
        open_state = PhilipsHueState.OPEN
        client.set_color(light_id, open_state.value)  # set to red
        return open_state
    if incident_state == "closed":
        closed_state = PhilipsHueState.CLOSED
        client.set_color(light_id, closed_state.value)  # set to green
        return closed_state
    else:
        raise UnknownIncidentStateError(f'Incident state must be "open" or "closed"; actual: {incident_state}')
