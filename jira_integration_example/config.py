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

"""Flask config for Jira integration."""

import os
from dotenv import load_dotenv
from utilities import secrets

load_dotenv()

class JiraConfig:
    """Base Jira config."""

    FLASK_ENV = 'production'
    LOGGING_LEVEL = 'INFO'
    TESTING = False
    DEBUG = False
    JIRA_CLOSED_INCIDENT_STATUS = 'Done'



class ProdJiraConfig(JiraConfig):
    """Production Jira config."""

    def __init__(self):
        self._jira_url = None
        self._jira_username = None
        self._jira_password = None
        self._jira_project = None


    @property
    def JIRA_URL(self):
        if self._jira_url is None:
            secret = secrets.GoogleSecretManagerSecret(
                'alertmanager-2020-intern-r', 'jira_url')
            self._jira_url = secret.get_secret_value()

        return self._jira_url


    @property
    def JIRA_USERNAME(self):
        if self._jira_username is None:
            secret = secrets.GoogleSecretManagerSecret(
                'alertmanager-2020-intern-r', 'jira_username')
            self._jira_username = secret.get_secret_value()

        return self._jira_username


    @property
    def JIRA_PASSWORD(self):
        if self._jira_password is None:
            secret = secrets.GoogleSecretManagerSecret(
                'alertmanager-2020-intern-r', 'jira_password')
            self._jira_password = secret.get_secret_value()

        return self._jira_password


    @property
    def JIRA_PROJECT(self):
        if self._jira_project is None:
            secret = secrets.GoogleSecretManagerSecret(
                'alertmanager-2020-intern-r', 'jira_project')
            self._jira_project = secret.get_secret_value()

        return self._jira_project



class DevJiraConfig(JiraConfig):
    """Development Jira config."""

    FLASK_ENV = 'development'
    LOGGING_LEVEL = 'DEBUG'
    DEBUG = True
    TESTING = True


    def __init__(self):
        self._jira_url = None
        self._jira_username = None
        self._jira_password = None
        self._jira_project = None


    @property
    def JIRA_URL(self):
        if self._jira_url is None:
            secret = secrets.EnvironmentVariableSecret('JIRA_URL')
            self._jira_url = secret.get_secret_value()

        return self._jira_url


    @property
    def JIRA_USERNAME(self):
        if self._jira_username is None:
            secret = secrets.EnvironmentVariableSecret('JIRA_USERNAME')
            self._jira_username = secret.get_secret_value()

        return self._jira_username


    @property
    def JIRA_PASSWORD(self):
        if self._jira_password is None:
            secret = secrets.EnvironmentVariableSecret('JIRA_PASSWORD')
            self._jira_password = secret.get_secret_value()

        return self._jira_password


    @property
    def JIRA_PROJECT(self):
        if self._jira_project is None:
            secret = secrets.EnvironmentVariableSecret('JIRA_PROJECT')
            self._jira_project = secret.get_secret_value()

        return self._jira_project



class TestJiraConfig(JiraConfig):
    """Test Jira config."""

    FLASK_ENV = 'test'
    LOGGING_LEVEL = 'DEBUG'
    DEBUG = True
    TESTING = True

    JIRA_CLOSED_INCIDENT_STATUS = 'Done'
    JIRA_URL = 'https://jira.atlassian.com'
    JIRA_USERNAME = 'test-user'
    JIRA_PASSWORD = 'test-password'
    JIRA_PROJECT = 'test-project'



_ENVIRONMENT_TO_CONFIG_MAPPING = {
    'prod': ProdJiraConfig,
    'dev': DevJiraConfig,
    'test': TestJiraConfig,
    'default': ProdJiraConfig
}



def load():
    environment_name = os.environ.get('FLASK_APP_ENV', 'default')
    return _ENVIRONMENT_TO_CONFIG_MAPPING[environment_name]()
