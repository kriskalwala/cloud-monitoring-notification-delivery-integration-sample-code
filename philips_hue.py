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

import os
import requests
import json


class PhilipsHueClient(object):
    def __init__(self, api_url):
        self.api_url = api_url
        

    def set_color(self, light_id, hue):
        """Sets the color of a Philips Hue light to a specified hue value.

        Args:
            light_id: The id to pass to the Philips Hue API to specify the light to set a color for.
            hue: Hue of the light. Takes values from 0 to 65535. 
                Programming 0 and 65535 would mean that the light will resemble 
                the color red, 21845 for green and 43690 for blue.

        Returns:
            HTTP Response from the Philips Hue API.
        """
        return requests.put(url = f'{self.api_url}/lights/{light_id}/state', data=json.dumps({"on": True, "hue": hue}))