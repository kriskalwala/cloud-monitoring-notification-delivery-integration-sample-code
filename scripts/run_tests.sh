#!/bin/bash

python3 -m pip3 install --upgrade pip3
pip3 install -r philips_hue_integration_example/requirements.txt
pip3 install -r jira_integration_example/requirements.txt

export FLASK_APP_ENV=test
pytest philips_hue_integration_example
pytest jira_integration_example