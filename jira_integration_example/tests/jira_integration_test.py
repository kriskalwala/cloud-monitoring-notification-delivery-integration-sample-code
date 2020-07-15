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
from pytest_mock import mocker

from utilities import jira_integration
from jira import JIRA


def test_update_jira_with_open_incident(mocker):
    jira_client = mocker.create_autospec(JIRA, instance=True)

    jira_project = 'test_project'
    notification = {'incident': {'state': 'open', 'condition_name': 'test_condition',
                                 'resource_name': 'test_resource', 'summary': 'test_summary',
                                 'url': 'http://test.com'}}

    expected_summary = '%s - %s' % (notification['incident']['condition_name'],
                                    notification['incident']['resource_name'])
    expected_description = '%s\nSee: %s' % (notification['incident']['summary'],
                                            notification['incident']['url'])
    expected_issue_type = {'name': 'Bug'}

    jira_integration.update_jira_based_on_monitoring_notification(jira_client, jira_project,
                                                                  notification)

    jira_client.create_issue.assert_called_once_with(project=jira_project,
                                                     summary=expected_summary,
                                                     description=expected_description,
                                                     issuetype=expected_issue_type)


def test_update_jira_with_closed_incident(mocker):
    jira_client = mocker.create_autospec(JIRA, instance=True)

    jira_project = 'test_project'
    notification = {'incident': {'state': 'closed', 'condition_name': 'test_condition',
                                 'resource_name': 'test_resource', 'summary': 'test_summary',
                                 'url': 'http://test.com'}}

    jira_integration.update_jira_based_on_monitoring_notification(jira_client, jira_project,
                                                                  notification)

    jira_client.create_issue.assert_not_called()


def test_update_jira_with_invalid_incident_state(mocker):
    jira_client = mocker.create_autospec(JIRA, instance=True)
    jira_project = 'test_project'
    incident_state = 'unknown_state'
    notification = {'incident': {'state': incident_state, 'condition_name': 'test_condition',
                                     'resource_name': 'test_resource', 'summary': 'test_summary',
                                     'url': 'http://test.com'}}

    with pytest.raises(jira_integration.UnknownIncidentStateError) as e:
        assert jira_integration.update_jira_based_on_monitoring_notification(
            jira_client, jira_project, notification)

    expected_error_value = f'Incident state must be "open" or "closed"'
    assert str(e.value) == expected_error_value


def test_update_jira_with_missing_notification_data(mocker):
    jira_client = mocker.create_autospec(JIRA, instance=True)
    jira_project = 'test_project'
    notification = {'incident': {}}

    with pytest.raises(jira_integration.NotificationParseError) as e:
        assert jira_integration.update_jira_based_on_monitoring_notification(
            jira_client, jira_project, notification)

    expected_error_value = 'Notification is missing required dict key'
    assert str(e.value) == expected_error_value

