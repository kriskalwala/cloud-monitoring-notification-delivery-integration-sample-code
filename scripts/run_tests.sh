#!/bin/bash

export FLASK_APP_ENV=test
directories="philips_hue_integration_example jira_integration_example"

for directory in $directories; do
    pytest $directory
done
