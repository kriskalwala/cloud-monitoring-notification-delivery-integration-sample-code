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

"""Module to provide callback functions for mock HTTP requests to the Philips Hue API."""

import json


def mock_hue_put_response(request, context):
    """Callback for mocking a Philips Hue API response using the requests-mock library,
    specifically for a put request.

    See https://requests-mock.readthedocs.io/en/latest/response.html for usage details.

    Args:
        request: The requests.Request object that was provided.
        context: An object containing the collected known data about this response
        (headers, status_code, reason, cookies).

    Returns:
        The response text with confirmation of the arguments passed in.
    """
    try:
        base_path_index = request.url.index('/lights/')
    except ValueError:
        context.status_code = 400
        return 'invalid Philips Hue url'

    try:
        body_json = json.loads(request.body)
    except json.JSONDecodeError:
        context.status_code = 400
        return 'invalid put request body'

    context.status_code = 200

    base_path = request.url[base_path_index:]
    response = []
    for arg in body_json:
        response.append({'success':{f'{base_path}/{arg}': f'{body_json[arg]}'}})
    return str(response)
