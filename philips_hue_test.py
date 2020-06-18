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

# NOTE:
# These tests are unit tests for functions in philips_hue.py.

import requests
import os
import base64
from uuid import uuid4
from dotenv import load_dotenv

import pytest

import main
import philips_hue
import philips_hue_mock
        
        
@pytest.fixture
def config():
    main.app.config.from_object('config.DevConfig')
    return main.app.config


@pytest.fixture
def philips_hue_client(config):
    philips_hue_client = philips_hue.PhilipsHueClient(config['PHILIPS_HUE_URL'])
    return philips_hue_client


def test_set_color(philips_hue_client, requests_mock):  
    url = philips_hue_client.api_url
    requests_mock.put(f'{url}/lights/1/state', text=philips_hue_mock.mock_hue_put_response)
    r = philips_hue_client.set_color(1, 0)
    assert r.status_code == 200
    assert '{"on": true, "hue": 0}' == r.text
    
    
def test_trigger_hue_from_incident_open(philips_hue_client, requests_mock):
    response = {"condition": {"state": "open"}}
    
    url = philips_hue_client.api_url
    requests_mock.put(f'{url}/lights/1/state', text=philips_hue_mock.mock_hue_put_response)
    r = philips_hue.trigger_hue_from_incident(philips_hue_client, response, 1)
    assert r.status_code == 200
    assert '{"on": true, "hue": 0}' == r.text


def test_trigger_hue_from_incident_closed(philips_hue_client, requests_mock):
    response = {"condition": {"state": "closed"}}
    
    url = philips_hue_client.api_url
    requests_mock.put(f'{url}/lights/1/state', text=philips_hue_mock.mock_hue_put_response)
    r = philips_hue.trigger_hue_from_incident(philips_hue_client, response, 1)
    assert r.status_code == 200
    assert '{"on": true, "hue": 25500}' == r.text