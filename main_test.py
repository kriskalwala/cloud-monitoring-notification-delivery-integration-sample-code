# Copyright 2019 Google, LLC.
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

# Source code from https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/run/pubsub/main_test.py

# NOTE:
# These tests are unit tests that mock Pub/Sub.

import base64
from uuid import uuid4
import requests

import pytest

import main

import os

# TODO: make config loading centralized
from dotenv import load_dotenv

load_dotenv()
URL = os.environ.get("philips-url")


@pytest.fixture
def client():
    main.app.testing = True
    return main.app.test_client()


@pytest.fixture
def config():
    main.app.config.from_object('config.DevConfig')
    return main.app.config


def test_empty_payload(client):
    r = client.post('/', json='')
    assert r.status_code == 400


def test_invalid_payload(client):
    r = client.post('/', json={'nomessage': 'invalid'})
    assert r.status_code == 400


def test_invalid_mimetype(client):
    r = client.post('/', json="{ message: true }")
    assert r.status_code == 400


# TODO: change to call dispatch interface
def test_trigger_hue_from_incident_open(client):
    response = {"incident": {"condition": {"state": "open"}}}
    main.trigger_hue_from_incident(response, 1)
    
    # TODO: mock http request
    r = requests.get(f'{URL}/lights/1')
    assert r.status_code == 200
    
    light_info = r.json()
    
    assert light_info["state"]["on"] == True
    assert light_info["state"]["hue"] == 0


# TODO: change to call dispatch interface
def test_trigger_hue_from_incident_closed(client):
    response = {"incident": {"condition": {"state": "closed"}}}
    main.trigger_hue_from_incident(response, 1)
    
    # TODO: mock http request
    r = requests.get(f'{URL}/lights/1')
    assert r.status_code == 200
    
    light_info = r.json()
    
    assert light_info["state"]["on"] == True
    assert light_info["state"]["hue"] == 25500


def test_invalid_pubsub_message(client, capsys):
    r = client.post('/', json={'message': True})
    assert r.status_code == 400

    out, _ = capsys.readouterr()
    assert 'invalid Pub/Sub message format' in out
    
    
def test_nonstring_notification_message(client, capsys):
    r = client.post('/', json={'message': {'data': True}})
    assert r.status_code == 400

    out, _ = capsys.readouterr()
    assert 'notification should be base64-encoded' in out
    
    
def test_unicode_notification_message(client, capsys):
    data = '{"incident": {"condition": {"state": "open"}}}'
    
    r = client.post('/', json={'message': {'data': data}})
    assert r.status_code == 400
    
    out, _ = capsys.readouterr()
    assert 'notification should be base64-encoded' in out
    
    
def test_invalid_notification_message(client, capsys):
    response = 'invalid message'
    data = base64.b64encode(response.encode()).decode()
    
    r = client.post('/', json={'message': {'data': data}})
    assert r.status_code == 400
    
    out, _ = capsys.readouterr()
    assert 'notification could not be decoded to a JSON' in out
    
    
def test_invalid_incident_message(client, capsys):
    response = '{"invalid": "error"}'
    data = base64.b64encode(response.encode()).decode()
    
    r = client.post('/', json={'message': {'data': data}})
    assert r.status_code == 400
    
    out, _ = capsys.readouterr()
    assert 'invalid incident format' in out    


def test_open_alert_message(client, capsys):
    response = '{"incident": {"condition": {"state": "open"}}}'
    data = base64.b64encode(response.encode()).decode()

    r = client.post('/', json={'message': {'data': data}})
    assert r.status_code == 204

    # TODO: mock http request
    r = requests.get(f'{URL}/lights/1')
    assert r.status_code == 200
    
    light_info = r.json()
    
    assert light_info["state"]["on"] == True
    assert light_info["state"]["hue"] == 0
    
def test_closed_alert_message(client, capsys):
    response = '{"incident": {"condition": {"state": "closed"}}}'
    data = base64.b64encode(response.encode()).decode()

    r = client.post('/', json={'message': {'data': data}})
    assert r.status_code == 204

    # TODO: mock http request
    r = requests.get(f'{URL}/lights/1')
    assert r.status_code == 200
    
    light_info = r.json()
    
    assert light_info["state"]["on"] == True
    assert light_info["state"]["hue"] == 25500    