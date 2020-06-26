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

"""Unit tests for functions in philips_hue.py."""

import re

import pytest

import philips_hue
import philips_hue_mock


@pytest.fixture
def config():
    policy_hue_mapping = {
        'policy1': 65535,
        'policy2': 25500,
        'default': 56063
    }
    
    configs = {
        'BRIDGE_IP_ADDRESS': '127.0.0.1',
        'USERNAME': 'test-user',
        'POLICY_HUE_MAPPING': policy_hue_mapping
    }
    return configs


@pytest.fixture
def philips_hue_client(config):
    philips_hue_client = philips_hue.PhilipsHueClient(
        config['BRIDGE_IP_ADDRESS'], config['USERNAME'])
    return philips_hue_client


def test_set_color(philips_hue_client, requests_mock):
    bridge_ip_address = philips_hue_client.bridge_ip_address
    username = philips_hue_client.username
    matcher = re.compile(f'http://{bridge_ip_address}/api/{username}')
    requests_mock.register_uri('PUT', matcher,
                               text=philips_hue_mock.mock_hue_put_response)

    response = philips_hue_client.set_color('1', 0)

    assert response.status_code == 200
    assert "{'success': {'/lights/1/state/on': 'true'}}" in response.text
    assert "{'success': {'/lights/1/state/hue': '0'}}" in response.text


def test_trigger_from_incident_bad_url(config, philips_hue_client,
                                       requests_mock):
    notification = {'incident': {'policy_name': 'policy2'}}
    bridge_ip_address = philips_hue_client.bridge_ip_address
    username = philips_hue_client.username
    matcher = re.compile(f'http://{bridge_ip_address}/api/{username}')
    requests_mock.register_uri('PUT', matcher,
                               text=philips_hue_mock.mock_hue_put_response)

    with pytest.raises(philips_hue.BadAPIRequestError) as e:
        assert philips_hue.trigger_light_from_monitoring_notification(
            philips_hue_client, notification, 2, config["POLICY_HUE_MAPPING"])
    assert str(e.value) == 'invalid Philips Hue url'


def test_trigger_hue_with_nondefault_policy(config, philips_hue_client,
                                            requests_mock):
    test_policy_name = 'policy2'
    notification = {'incident': {'policy_name': test_policy_name}}
    bridge_ip_address = philips_hue_client.bridge_ip_address
    username = philips_hue_client.username
    matcher = re.compile(f'http://{bridge_ip_address}/api/{username}')
    requests_mock.register_uri('PUT', matcher,
                               text=philips_hue_mock.mock_hue_put_response)

    response = philips_hue.trigger_light_from_monitoring_notification(
        philips_hue_client, notification, 1, config["POLICY_HUE_MAPPING"])

    assert response == config['POLICY_HUE_MAPPING'][test_policy_name]


def test_trigger_hue_with_default_policy(config, philips_hue_client,
                                         requests_mock):
    test_policy_name = 'unknown_policy'
    notification = {'incident': {'policy_name': test_policy_name}}
    bridge_ip_address = philips_hue_client.bridge_ip_address
    username = philips_hue_client.username
    matcher = re.compile(f'http://{bridge_ip_address}/api/{username}')
    requests_mock.register_uri('PUT', matcher,
                               text=philips_hue_mock.mock_hue_put_response)

    response = philips_hue.trigger_light_from_monitoring_notification(
        philips_hue_client, notification, 1, config["POLICY_HUE_MAPPING"])

    assert response == config['POLICY_HUE_MAPPING']['default']
