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

"""Module to handle interactions with a Jira server.

This module defines a function to interact with Jira server when a
monitoring notification occurs. In addition, it defines error
classes to be used by the function.
"""

from jira import JIRA
import logging

logger = logging.getLogger(__name__)


class Error(Exception):
    """Base class for all errors raised in this module."""


class NotificationParseError(Error):
    """Exception raised for errors in a monitoring notification format."""


class UnknownIncidentStateError(Error):
    """Exception raised for errors in an invalid incident state value."""


def update_jira_based_on_monitoring_notification(jira_url, jira_project,
                                                 jira_username, jira_password,
                                                 notification):
    """Updates a Jira server based off the data in a monitoring notification.

    If the monitoring notification is about an open incident, a new issue (of
    type bug) is created on the specified Jira server under the specified
    jira project.

    Args:
        jira_url: The URL to the Jira server in which to create the issue.
        jira_project: The key or id of the Jira project under which to create
            the Jira issue.
        jira_username: Username of the account to use to access the Jira server
            and create the Jira issue.
        jira_password: Password of the account to use to access the Jira server
            and create the Jira issue.
        notification: The dictionary containing the notification data.

    Raises:
        UnknownIncidentStateError: If the incident state is not open or closed.
        NotificationParseError: If notification is missing required dict key.
        JIRAError: If error occurs when initializing or using the jira client
    """

    try:
        incident_data = notification['incident']
        incident_state = incident_data['state']
        incident_condition_name = incident_data['condition_name']
        incident_resource_name = incident_data['resource_name']
        incident_summary = incident_data['summary']
        incident_url = incident_data['url']
    except KeyError:
        raise NotificationParseError("Notification is missing required dict key")

    if incident_state == 'open':
        jira_client = JIRA(jira_url, basic_auth=(jira_username, jira_password))
        
        summary = '%s - %s' % (incident_condition_name, incident_resource_name)
        description = '%s\nSee: %s' % (incident_summary, incident_url)
        issue = jira_client.create_issue(
            project=jira_project,
            summary=summary,
            description=description,
            issuetype={'name': 'Bug'})
        logger.info('Created jira issue %s', issue)
    elif incident_state != 'closed':
        raise UnknownIncidentStateError(
            f'Condition state must be "open" or "closed"')
