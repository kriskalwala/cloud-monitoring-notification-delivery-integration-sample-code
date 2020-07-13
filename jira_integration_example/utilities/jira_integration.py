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

import logging

logger = logging.getLogger(__name__)

def update_jira_based_on_monitoring_notification(jira_client, jira_project, notification):
    incident_data = notification['incident']

    if incident_data['state'] == 'open':
        summary = '%s - %s' % (incident_data['condition_name'],
                               incident_data['resource_name'])
        description = '%s\nSee: %s' % (incident_data['summary'],
                                       incident_data['url'])
        issue = jira_client.create_issue(
            project=jira_project,
            summary=summary,
            description=description,
            issuetype={'name': 'Bug'})
        logger.info('Created jira issue %s', issue)
