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

import os
import requests
import json


class PhilipsHueClient(object):    
    def __init__(self, bridge_ip_address, username):
        self.bridge_ip_address = bridge_ip_address
        self.username = username
        
    
    def lights():
        response = requests.get(f'http://{self.bridge_ip_address}/api/{self.username}/lights')
        
        lights_dict = {}
        for light_id in response:
            lights_dict[light_id] = Light(light_id)
        
        lights = HueLights(lights_dict)
        return lights
    
    
class HueLights():
    def __init__(self, lights):
        self.lights = lights

        
    def get(light_id):
        return self.lights[light_id]
    
    
    def __iter__():
        for light in self.lights:
            yield self.lights[light]
        
    
    
class Light():
    def __init__(self, light_id):
        self.light_id = light_id
        

    def set_color(self, hue):
        """Sets the color of the light to a specified hue value.

        Args:
            hue: Hue of the light. Takes values from 0 to 65535. 
                Programming 0 and 65535 would mean that the light will resemble 
                the color red, 21845 for green and 43690 for blue.

        Returns:
            HTTP Response from the Philips Hue API.
        """
        return requests.put(url = f'http://{self.bridge_ip_address}/api/{self.username}/lights/{light_id}/state', 
                            data=json.dumps({"on": True, "hue": hue}))
    
    
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
        
    Raises:
        ValueError: If the incident state is not open or closed.
    """
    condition_state = incident["condition"]["state"]
    if condition_state == "open":
        return client.set_color(light_id, 0)  # set to red
    elif condition_state == "closed":
        return client.set_color(light_id, 25500)  # set to green
    else:
        raise ValueError("incident state should be either open or closed") 