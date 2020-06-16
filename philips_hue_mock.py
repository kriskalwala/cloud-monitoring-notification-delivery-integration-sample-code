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

def mock_hue_put_response(request, context):
    """Callback for mocking a Philips Hue API response using the requests-mock library, specifically for a put request.
    
    See https://requests-mock.readthedocs.io/en/latest/response.html for usage details.

    Args:
        request: The requests.Request object that was provided.
        context: An object containing the collected known data about this response
        (headers, status_code, reason, cookies).
        
    Returns:
        The response text.
    """
    if request.body:
        context.status_code = 200
        return request.body
    else:
        context.status_code = 400
        return 'invalid put request'