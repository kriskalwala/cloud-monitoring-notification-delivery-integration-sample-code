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
    philips_hue_client = philips_hue.PhilipsHueClient(
        config['BRIDGE_IP_ADDRESS'], config['USERNAME'])
    return philips_hue_client


def test_set_color(philips_hue_client, requests_mock):
    bridge_ip_address = philips_hue_client.bridge_ip_address
    username = philips_hue_client.username

    requests_mock.put(f'http://{bridge_ip_address}/api/{username}/lights/1/state',
                      text=philips_hue_mock.mock_hue_put_response)
    response = philips_hue_client.set_color('1', 0)
    assert response.status_code == 200
    assert "{'success': {'/lights/1/state/on': 'True'}}" in response.text
    assert "{'success': {'/lights/1/state/hue': '0'}}" in response.text


def test_trigger_hue_from_incident_open(philips_hue_client, requests_mock):
    response = {"incident": {"condition": {"state": "open"}}}

    bridge_ip_address = philips_hue_client.bridge_ip_address
    username = philips_hue_client.username

    requests_mock.put(f'http://{bridge_ip_address}/api/{username}/lights/1/state',
                      text=philips_hue_mock.mock_hue_put_response)
    response = philips_hue.trigger_light_from_monitoring_notification(
        philips_hue_client, response, 1)
    assert response.status_code == 200
    assert "{'success': {'/lights/1/state/on': 'True'}}" in response.text
    assert "{'success': {'/lights/1/state/hue': '0'}}" in response.text


def test_trigger_hue_from_incident_closed(philips_hue_client, requests_mock):
    response = {"incident": {"condition": {"state": "closed"}}}

    bridge_ip_address = philips_hue_client.bridge_ip_address
    username = philips_hue_client.username

    requests_mock.put(f'http://{bridge_ip_address}/api/{username}/lights/1/state',
                      text=philips_hue_mock.mock_hue_put_response)
    response = philips_hue.trigger_light_from_monitoring_notification(
        philips_hue_client, response, 1)
    assert response.status_code == 200
    assert "{'success': {'/lights/1/state/on': 'True'}}" in response.text
    assert "{'success': {'/lights/1/state/hue': '25500'}}" in response.text
