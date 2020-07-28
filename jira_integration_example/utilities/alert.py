# Copyright 2020 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import time

from google.cloud import monitoring_v3
from google.protobuf import Duration


PROJECT_ID = os.environ['GOOGLE_CLOUD_PROJECT']
TRIGGER_VALUE = 3.0


class TestCustomMetricClient():
    """Client that can create and modify custom metrics
    used as monitoring data for testing purposes.
    
    Attributes:
        _project_id: The id of the project to store metrics
        _client: A monitoring_v3.MetricServiceClient instance to modify metric data
    """
    
    def __init__(self, project_id):
        self._project_id = project_id
        self._client = monitoring_v3.MetricServiceClient()
        
        
    def create_custom_metric(self, metric_name):
        # [START monitoring_create_metric]
        project_name = self._client.project_path(self._project_id)
        descriptor = monitoring_v3.types.MetricDescriptor()
        descriptor.type = 'custom.googleapis.com/' + metric_name
        descriptor.metric_kind = (
            monitoring_v3.enums.MetricDescriptor.MetricKind.GAUGE)
        descriptor.value_type = (
            monitoring_v3.enums.MetricDescriptor.ValueType.DOUBLE)
        descriptor.description = 'A custom metric meant for testing purposes'
        descriptor = self._client.create_metric_descriptor(project_name, descriptor)
        print('Created {}.'.format(descriptor.name))
        # [END monitoring_create_metric]


    def append_to_time_series(self, metric_name, point_value):
        # [START monitoring_write_timeseries]
        project_name = self._client.project_path(self._project_id)

        series = monitoring_v3.types.TimeSeries()
        series.metric.type = 'custom.googleapis.com/' + metric_name
        series.resource.type = 'gce_instance'
        series.resource.labels['instance_id'] = '1234567890123456789'
        series.resource.labels['zone'] = 'us-central1-f'
        point = series.points.add()
        point.value.double_value = point_value
        now = time.time()
        point.interval.end_time.seconds = int(now)
        point.interval.end_time.nanos = int(
            (now - point.interval.end_time.seconds) * 10**9)
        self._client.create_time_series(project_name, [series])
        # [END monitoring_write_timeseries]


class TestPolicyClient():
    """Client that can create and modify alerting policies and
    trigger/resolve incidents for testing purposes.
    
    Attributes:
        _project_id: The id of the project to add or modify policies to
        _policy_client: A monitoring_v3.AlertPolicyServiceClient instance to call the alertPolicies API
        _metric_client: A TestCustomMetricClient() instance to modify metric data 
        to trigger/resolve incidents
        _threshold_value: Value above which a policy triggers an incident
    """
    
    def __init__(self, project_id):
        self._project_id = project_id
        self._policy_client = monitoring_v3.AlertPolicyServiceClient()
        self._metric_client = TestCustomMetricClient(self._project_id)
        self._threshold_value = 3.0
        
    
    def create_policy(self, display_name, metric_name):
        """Creates an alert policy with the given display name.
        By default, a policy is made with a single condition that triggers
        if a custom metric with the given metric name is above the threshold value.
        
        Args:
            display_name: the name to identify the policy by
            metric_name: metric to attach the policy to
        """
        name = self._policy_client.project_path(self._project_id)
        # TODO: fill in
        condition_threshold = monitoring_v3.types.AlertPolicy.Condition.MetricThreshold(
            filter=f'metric.type = "custom.googleapis.com/${metric_name}" AND resource.type = "gce_instance"',
            comparison=monitoring_v3.enums.ComparisonType.COMPARISON_GT,
            threshold_value=self._threshold_value,
            duration=Duration(seconds=0)
        )
        condition = monitoring_v3.types.AlertPolicy.Condition(condition_threshold=condition_threshold)
        alert_policy = monitoring_v3.types.AlertPolicy(
            display_name=display_name,
            conditions=[condition])
        self._policy_client.create_alert_policy(name, alert_policy)
    

    def trigger_incident(self, metric_name):
        append_to_time_series(PROJECT_ID, metric_name, TRIGGER_VALUE + 1)
    
    
    def resolve_incident(self, metric_name):
        append_to_time_series(PROJECT_ID, metric_name, TRIGGER_VALUE - 1)


def main():
    client = TestPolicyClient('alertmanager-cloudmon-test')
    client.create_policy('test', 'custom_metric')
    
    

if __name__ == '__main__':
    main()