#!/usr/bin/python3
#
# Copyright 2020 Google LLC.
# SPDX-License-Identifier: Apache-2.0
#
##
# Summary:
#  This is an example script that forwards alerts from GCP to Jira.
#
# Dependencies:
#  pip3 install futures jira google-cloud-pubsub
#
# Usage:
#  Fill in the following environment variables (or replace those lines below):
#   PUBSUB_PROJECT: The gcp project that is sending the pubsub messages.
#   PUBSUB_SUB: The subscription id that will be used to receive messages.
#   JIRA_URL: The url of the jira server (ie http://localhost:8080).
#   JIRA_USERNAME: The username of the jira account to use for creating issues.
#   JIRA_PASSWORD: The password of the jira account to use for creating issues.
#   JIRA_PROJECT: The ID of the jira project to publish events to.
#  python3 jira_pubsub.py
#
# References:
#  Google pubsub pull: https://cloud.google.com/pubsub/docs/pull
#  Jira library: https://jira.readthedocs.io/

import concurrent.futures
import json
import logging
import os
from google.cloud import pubsub_v1
from jira import JIRA

logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename='cloud-alert-jira.log',
                    level=logging.INFO)

# google pubsub settings
project_id = os.environ['PUBSUB_PROJECT']
subscription_id = os.environ['PUBSUB_SUB']
# Number of seconds the subscriber should listen for messages
timeout = None

# jira settings
jira_url = os.environ['JIRA_URL']
jira_username = os.environ['JIRA_USERNAME']
jira_password = os.environ['JIRA_PASSWORD']
jira_project = os.environ['JIRA_PROJECT']

# Use basic authentication for this demo.
# For information on better authentication methods see:
# https://jira.readthedocs.io/en/master/examples.html#authentication
jira = JIRA(jira_url, basic_auth=(jira_username, jira_password))


# Called for every published message.
def callback(message):
    data = json.loads(message.data)['incident']
    logging.info('Received pubsub incident %s', data)
    # Ignore anything but new issues.
    # A more advanced implementation could update or close existing jira issues
    # based on the state field and a jira-google issue id mapping.
    if data['state'] == 'open':
        summary = '%s - %s' % (data['condition_name'], data['resource_name'])
        description = '%s\nSee: %s' % (data['summary'], data['url'])
        issue = jira.create_issue(
            project=jira_project,
            summary=summary,
            description=description,
            issuetype={'name': 'Bug'})
        logging.info('Created jira issue %s', issue)
    message.ack()


subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)
streaming_pull_future = subscriber.subscribe(
    subscription_path, callback=callback)
print('Listening for messages on %s..' % subscription_path)

# Wrap subscriber in a 'with' block to automatically call close() when done.
with subscriber:
    try:
        # When `timeout` is not set, result() will block indefinitely,
        # unless an exception is encountered first.
        streaming_pull_future.result(timeout=timeout)
    except concurrent.futures.TimeoutError:
        streaming_pull_future.cancel()
