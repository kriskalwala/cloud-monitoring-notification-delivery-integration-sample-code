# Copyright 2017 Google Inc.
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

# Source code based off of
# https://github.com/googleinterns/cloud-monitoring-notification-delivery-integration-sample-code/blob/server-setup/main.py

"""Use custom metric to trigger and resolve incidents.

This program has can perform 3 operations depending on
the argument that is given: create a new custom metric
called "testing_metric", trigger an incident, or resolve
the incident. To use it correctly, first create the custom
metric (only do this once). Then in the GCP website create a
policy where the metric is "testing_metric" and the resource
type is "GCE VM Instance", and set it to trigger when the
most recent value of any time series is above 3.0 (only create
the policy once). Once the custom metric and policy are
created, the program can properly trigger and resolve an
incident on command.


  How to use:

  $ python3 trigger_incident.py -h
  $ python3 trigger_incident.py create-custom-metric
  $ python3 trigger_incident.py trigger-incident
  $ python3 trigger_incident.py resolve-incident
"""

import argparse
import os
import pprint
import time

from google.cloud import monitoring_v3


PROJECT_ID = os.environ['GOOGLE_CLOUD_PROJECT']


def create_custom_metric(project_id, metric_name):
    # [START monitoring_create_metric]
    client = monitoring_v3.MetricServiceClient()
    project_name = client.project_path(project_id)
    descriptor = monitoring_v3.types.MetricDescriptor()
    descriptor.type = 'custom.googleapis.com/' + metric_name
    descriptor.metric_kind = (
        monitoring_v3.enums.MetricDescriptor.MetricKind.GAUGE)
    descriptor.value_type = (
        monitoring_v3.enums.MetricDescriptor.ValueType.DOUBLE)
    descriptor.description = 'A custom metric meant for testing purposes'
    descriptor = client.create_metric_descriptor(project_name, descriptor)
    print('Created {}.'.format(descriptor.name))
    # [END monitoring_create_metric]


def append_to_time_series(project_id, metric_name, point_value):
    # [START monitoring_write_timeseries]
    client = monitoring_v3.MetricServiceClient()
    project_name = client.project_path(project_id)

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
    client.create_time_series(project_name, [series])
    # [END monitoring_write_timeseries]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Create a custom metric and use it to trigger and resolve incidents')

    subparsers = parser.add_subparsers(dest='command')

    create_metric_descriptor_parser = subparsers.add_parser(
        'create-custom-metric',
        help='create a custom metric type called "testing_metric"'
    )

    write_time_series_parser = subparsers.add_parser(
        'trigger-incident',
        help='trigger incident by appending new data point (of value 4.0) to "testing_metric" time series'
    )

    write_time_series_parser = subparsers.add_parser(
        'resolve-incident',
        help='resolve incident by appending new data point (of value 2.0) to "testing_metric" time series'
    )

    args = parser.parse_args()

    if args.command == 'create-custom-metric':
        create_custom_metric(PROJECT_ID, 'testing_metric')
    if args.command == 'trigger-incident':
        append_to_time_series(PROJECT_ID, 'testing_metric', 4.0)
    if args.command == 'resolve-incident':
        append_to_time_series(PROJECT_ID, 'testing_metric', 2.0)
    if args.command is None:
        print('To see available arguments, use $ python3 trigger_incident.py -h')
