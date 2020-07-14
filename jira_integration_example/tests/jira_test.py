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


def test_update_jira_with_open_incident(mocker):
    jira_url = 'http://test-jira.com'
    jira_project = 'test_project'
    jira_username = 'test_username'
    jira_password = 'test_password'
    notification = {'incident': {'state': 'open', 'condition_name': 'test_condition',
                                 'resource_name': 'test_resource', 'summary': 'test_summary',
                                 'url': 'http://test-cloud.com'}}

    expected_summary = '%s - %s' % (notification['incident']['condition_name'],
                                    notification['incident']['resource_name'])
    expected_description = '%s\nSee: %s' % (notification['incident']['summary'], 
                                            notification['incident']['url'])
    expected_issue_type = {'name': 'Bug'}
    
    mocker.patch(f"{__name__}.jira_integration.JIRA", autospec=True)
    jira_client = jira_integration.JIRA.return_value # jira client used by update_jira function

    jira_integration.update_jira_based_on_monitoring_notification(jira_url, jira_project,
                                                                  jira_username, jira_password,
                                                                  notification)

    jira_client.create_issue.assert_called_once_with(project=jira_project,
                                                     summary=expected_summary,
                                                     description=expected_description,
                                                     issuetype=expected_issue_type)


def test_update_jira_with_closed_incident(mocker):
    jira_url = 'http://test-jira.com'
    jira_project = 'test_project'
    jira_username = 'test_username'
    jira_password = 'test_password'
    notification = {'incident': {'state': 'closed', 'condition_name': 'test_condition',
                                 'resource_name': 'test_resource', 'summary': 'test_summary',
                                 'url': 'http://test-cloud.com'}}

    mocker.patch(f"{__name__}.jira_integration.JIRA", autospec=True)
    jira_client = jira_integration.JIRA.return_value

    jira_integration.update_jira_based_on_monitoring_notification(jira_url, jira_project,
                                                                      jira_username, jira_password,
                                                                      notification)

    jira_client.create_issue.assert_not_called()


def test_update_jira_with_invalid_incident_state():
    jira_url = 'http://test-jira.com'
    jira_project = 'test_project'
    jira_username = 'test_username'
    jira_password = 'test_password'
    incident_state = 'unknown_state'
    notification = {'incident': {'state': incident_state, 'condition_name': 'test_condition',
                                     'resource_name': 'test_resource', 'summary': 'test_summary',
                                     'url': 'http://test-cloud.com'}}

    with pytest.raises(jira_integration.UnknownIncidentStateError) as e:
        assert jira_integration.update_jira_based_on_monitoring_notification(
            jira_url, jira_project, jira_username, jira_password, notification)

    expected_error_value = f'Condition state must be "open" or "closed"'
    assert str(e.value) == expected_error_value


def test_update_jira_with_missing_notification_data():
    jira_url = 'http://test-jira.com'
    jira_project = 'test_project'
    jira_username = 'test_username'
    jira_password = 'test_password'
    notification = {'invalid': 'error'}

    with pytest.raises(jira_integration.NotificationParseError) as e:
        assert jira_integration.update_jira_based_on_monitoring_notification(
            jira_url, jira_project, jira_username, jira_password, notification)

    expected_error_value = 'Notification is missing required dict key'
    assert str(e.value) == expected_error_value

