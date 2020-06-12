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

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
URL = os.environ.get("philips-url")


def set_color(light_id, hue):
    """Sets the color of a Philips Hue light to a specified hue value.

    Args:
        light_id: The id of the light to set the color for.
        hue: Hue of the light.
    """
    r = requests.put(url = f'{URL}/lights/{light_id}/state', data=json.dumps({"on": True, "hue": hue}))