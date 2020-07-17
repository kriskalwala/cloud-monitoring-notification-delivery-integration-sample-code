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

import logging
logger = logging.getLogger(__name__)


class Error(Exception):
    """Base class for all errors raised in this module."""


class NotificationParseError(Error):
    """Exception raised for errors in a monitoring notification format."""


class UnknownIncidentStateError(Error):
    """Exception raised for errors in an invalid incident state value."""


def update_jira_based_on_monitoring_notification(jira_client, jira_project,
                                                 notification):
    """Updates a Jira server based off the data in a monitoring notification.

    If the monitoring notification is about an open incident, a new issue (of
    type bug) is created on the jira server that the jira client is connected
    to under the specified jira project.

    Args:
        jira_client: A JIRA object that acts as a client which allows
            interaction with a specific Jira server. It is used to create
            the new Jira issue.
        jira_project: The key or id of the Jira project under which to create
            the Jira issue.
        notification: The dictionary containing the notification data.

    Raises:
        UnknownIncidentStateError: If the incident state is not open or closed.
        NotificationParseError: If notification is missing required dict key.
        JIRAError: If error occurs when using the jira client
    """

    try:
        incident_data = notification['incident']
        incident_state = incident_data['state']
        incident_condition_name = incident_data['condition_name']
        incident_resource_name = incident_data['resource_name']
        incident_summary = incident_data['summary']
        incident_url = incident_data['url']
    except KeyError as e:
        raise NotificationParseError(f"Notification is missing required dict key: {str(e)}")

    if incident_state == 'open':
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
            'Incident state must be "open" or "closed"')
