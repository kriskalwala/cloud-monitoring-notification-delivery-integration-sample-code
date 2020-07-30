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

import pytest
import constants

from google.cloud import monitoring_v3
from google.protobuf.duration_pb2 import Duration
from google.api_core import exceptions
from google.api_core import retry


@retry.Retry(predicate=retry.if_exception_type(exceptions.NotFound), deadline=10)
def call_get_metric(metric_client, name):
    return metric_client.get_metric_descriptor(name)


@retry.Retry(predicate=retry.if_exception_type(exceptions.NotFound), deadline=10)
def call_get_alert_policy(policy_client, name):
    return policy_client.get_alert_policy(name)


@retry.Retry(predicate=retry.if_exception_type(exceptions.NotFound), deadline=10)
def call_get_notification_channel(notification_channel_client, name):
    return notification_channel_client.get_notification_channel(name)


@pytest.fixture(scope='function')
def metric_descriptor():
    # setup
    metric_client = monitoring_v3.MetricServiceClient()
    gcp_project_path = metric_client.project_path(constants.PROJECT_ID)
    
    metric_descriptor = metric_client.create_metric_descriptor(
        gcp_project_path,
        constants.TEST_METRIC_DESCRIPTOR)   
    metric_descriptor = call_get_metric(metric_client, metric_descriptor.name)
    
    yield metric_descriptor
    
    # tear down
    metric_client.delete_metric_descriptor(metric_descriptor.name)
    
    
@pytest.fixture(scope='function')
def notification_channel():
    # setup
    notification_channel_client = monitoring_v3.NotificationChannelServiceClient()
    gcp_project_path = notification_channel_client.project_path(constants.PROJECT_ID)
    
    notification_channel = notification_channel_client.create_notification_channel(
        gcp_project_path,
        constants.TEST_NOTIFICATION_CHANNEL)
    notification_channel = call_get_notification_channel(notification_channel_client, notification_channel.name)
    
    yield notification_channel
    
    # tear down
    notification_channel_client.delete_notification_channel(notification_channel.name)


@pytest.fixture(scope='function')
def alert_policy_resources(metric_desciptor, notification_channel):
    # setup
    policy_client = monitoring_v3.AlertPolicyServiceClient()
    gcp_project_path = policy_client.project_path(constants.PROJECT_ID)
    
    print(metric_descriptor.name)
    print(notification_channel.name)

    alert_policy = policy_client.create_alert_policy(
        gcp_project_path,
        constants.TEST_ALERT_POLICY)
    alert_policy = call_get_alert_policy(policy_client, alert_policy.name)

    yield {'metric_descriptor': metric_descriptor,
           'notification_channel': notification_channel,
           'alert_policy': alert_policy}
    
    # tear down
    policy_client.delete_alert_policy(alert_policy.name)


def test_end_to_end(alert_policy_resources):
    metric_descriptor = alert_policy_resources['metric_descriptor']
    notification_channel = alert_policy_resources['notification_channel']
    alert_policy = alert_policy_resources['alert_policy']
    
    assert metric_descriptor.type == constants.TEST_METRIC_DESCRIPTOR['type']
    assert notification_channel.display_name == constants.TEST_NOTIFICATION_CHANNEL['display_name']
    assert alert_policy.display_name == constants.ALERT_POLICY_NAME
    assert alert_policy.user_labels == constants.TEST_ALERT_POLICY['user_labels']
    assert alert_policy.notification_channels[0].labels == constants.TEST_NOTIFICATION_CHANNEL['labels']
    
    