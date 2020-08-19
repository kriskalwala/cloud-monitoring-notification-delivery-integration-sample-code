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

import time

import pytest

from google.cloud import monitoring_v3
from google.api_core import exceptions
from google.api_core import retry
from jira import JIRA

import main
from tests import constants


@retry.Retry(predicate=retry.if_exception_type(exceptions.NotFound), deadline=10)
def short_retry(callable_function, *args):
    return callable_function(*args)


@retry.Retry(predicate=retry.if_exception_type(AssertionError), deadline=180)
def long_retry(callable_function, *args):
    return callable_function(*args)


@pytest.fixture
def config():
    return main.app.config


@pytest.fixture(scope='function')
def jira_client(config):
    # setup
    oauth_dict = {'access_token': config['JIRA_ACCESS_TOKEN'],
                  'access_token_secret': config['JIRA_ACCESS_TOKEN_SECRET'],
                  'consumer_key': config['JIRA_CONSUMER_KEY'],
                  'key_cert': config['JIRA_KEY_CERT']}
    jira_client = JIRA(config['JIRA_URL'], oauth=oauth_dict)                                         

    yield jira_client

    # tear down
    project_id = config['PROJECT_ID']
    test_issues = jira_client.search_issues(f'description~"custom/integ-test-metric for {project_id}"')
    for issue in test_issues:
        issue.delete()


@pytest.fixture(scope='function')
def metric_descriptor(config, metric_name):
    # setup
    metric_client = monitoring_v3.MetricServiceClient()
    gcp_project_path = metric_client.project_path(config['PROJECT_ID'])
        
    test_metric_descriptor = constants.TEST_METRIC_DESCRIPTOR_TEMPLATE
    test_metric_descriptor['type'] = constants.TEST_METRIC_DESCRIPTOR_TEMPLATE['type'].format(METRIC_NAME=metric_name)

    metric_descriptor = metric_client.create_metric_descriptor(
        gcp_project_path,
        test_metric_descriptor)
    metric_descriptor = short_retry(metric_client.get_metric_descriptor, metric_descriptor.name)

    yield metric_descriptor

    # tear down
    metric_client.delete_metric_descriptor(metric_descriptor.name)


@pytest.fixture(scope='function')
def notification_channel(config):
    # setup
    notification_channel_client = monitoring_v3.NotificationChannelServiceClient()
    gcp_project_path = notification_channel_client.project_path(config['PROJECT_ID'])
    test_notification_channel = constants.TEST_NOTIFICATION_CHANNEL_TEMPLATE
    test_notification_channel['labels']['topic'] = constants.TEST_NOTIFICATION_CHANNEL_TEMPLATE['labels']['topic'].format(PROJECT_ID=config['PROJECT_ID'])

    notification_channel = notification_channel_client.create_notification_channel(
        gcp_project_path,
        test_notification_channel)
    notification_channel = short_retry(notification_channel_client.get_notification_channel,
                                       notification_channel.name)

    yield notification_channel

    # tear down
    notification_channel_client.delete_notification_channel(notification_channel.name)


@pytest.fixture(scope='function')
def alert_policy(config, notification_channel, alert_policy_name, metric_name):
    # setup
    policy_client = monitoring_v3.AlertPolicyServiceClient()
    gcp_project_path = policy_client.project_path(config['PROJECT_ID'])

    test_alert_policy = constants.TEST_ALERT_POLICY_TEMPLATE
    test_alert_policy['notification_channels'].append(notification_channel.name)
    test_alert_policy['display_name'] = alert_policy_name
    test_alert_policy['user_labels']['metric'] = metric_name
    metric_path = constants.METRIC_PATH.format(METRIC_NAME=metric_name)
    test_alert_policy['conditions'][0]['condition_threshold']['filter'] = test_alert_policy['conditions'][0]['condition_threshold']['filter'].format(METRIC_PATH=metric_path)

    alert_policy = policy_client.create_alert_policy(
        gcp_project_path,
        test_alert_policy)
    alert_policy = short_retry(policy_client.get_alert_policy, alert_policy.name)

    yield alert_policy

    # tear down
    policy_client.delete_alert_policy(alert_policy.name)


def append_to_time_series(config, point_value):
    client = monitoring_v3.MetricServiceClient()
    gcp_project_path = client.project_path(config['PROJECT_ID'])

    series = monitoring_v3.types.TimeSeries()
    series.metric.type = constants.METRIC_PATH
    series.resource.type = constants.RESOURCE_TYPE
    series.resource.labels['instance_id'] = constants.INSTANCE_ID
    series.resource.labels['zone'] = constants.ZONE
    point = series.points.add()
    point.value.double_value = point_value
    now = time.time()
    point.interval.end_time.seconds = int(now)
    point.interval.end_time.nanos = int(
        (now - point.interval.end_time.seconds) * 10**9)

    client.create_time_series(gcp_project_path, [series])


@pytest.mark.parametrize('metric_name,alert_policy_name', [('integ-test-metric','integ-test-policy')])
def test_open_close_ticket(config, metric_descriptor, notification_channel, alert_policy, jira_client):
    # Sanity check that the test fixtures were initialized with values that the rest of the test expects
    assert metric_descriptor.type == constants.TEST_METRIC_DESCRIPTOR_TEMPLATE['type'].format(METRIC_NAME='integ-test-metric')
    assert notification_channel.display_name == constants.TEST_NOTIFICATION_CHANNEL_TEMPLATE['display_name']
    assert alert_policy.display_name == 'integ-test-policy'
    assert alert_policy.notification_channels[0] == notification_channel.name

    def assert_jira_issue_is_created():
        # Search for all issues where the status is 'unresolved' and
        # the integ-test-metric custom field is set to this the Cloud Monitoring project ID
        project_id = config['PROJECT_ID']
        query_string = f'description~"custom/integ-test-metric for {project_id}" and status=10000'
        created_monitoring_issues = jira_client.search_issues(query_string)
        assert len(created_monitoring_issues) == 1

    def assert_jira_issue_is_resolved():
        # Search for all issues where the status is 'resolved' and
        # the integ-test-metric custom field is set to this the Cloud Monitoring project ID
        project_id = config['PROJECT_ID']
        query_string = f'description~"custom/integ-test-metric for {project_id}" and status={config["CLOSED_JIRA_ISSUE_STATUS"]}'
        resolved_monitoring_issues = jira_client.search_issues(query_string)
        assert len(resolved_monitoring_issues) == 1

    # trigger incident and check jira issue created
    append_to_time_series(config, constants.TRIGGER_NOTIFICATION_THRESHOLD_DOUBLE + 1)
    long_retry(assert_jira_issue_is_created) # issue status id for "To Do"

    # resolve incident and check jira issue resolved
    append_to_time_series(config, constants.TRIGGER_NOTIFICATION_THRESHOLD_DOUBLE)
    long_retry(assert_jira_issue_is_resolved)
    