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

"""Represents and allows the access of secret values

This module contains classes that represent a secret
stored in a specific location and that have a method
to access the secret value.

Typical usage example:

  secret = EnvironmentVariableSecret(secret_name)
  secret_value = secret.get_secret_value()
"""

import abc
import os
from google.cloud import secretmanager


class Secret(abc.ABC):
    """Abstract base class that represents a secret and
    allows access to the secret value.

    """

    @abc.abstractmethod
    def get_secret_value():
        pass



class EnvironmentVariableSecret(Secret):
    """Represents a secret stored in the evironment of a specified
    name. Allows access to the secret value.

    Attributes:
        secret_name: The name of the secret
    """

    def __init__(self, secret_name):
        self.secret_name = secret_name


    def get_secret_value(self):
        return os.environ.get(self.secret_name)



class GoogleSecretManagerSecret(Secret):
    """Represents a secret stored in Google Secret Manager
    of a specified name. Allows access to the secret value.

    Attributes:
        project_id: The id of the project that the secret manager is in
        secret_name: The name of the secret
        version: the version of the secret
        client: The secret manager client to use to access the secret

    """

    def __init__(self, project_id, secret_name, version='latest', client=None):
        self.project_id = project_id
        self.secret_name = secret_name
        self.version = version
        self.client = client


    def get_secret_value(self):
        if self.client is None:
            self.client = secretmanager.SecretManagerServiceClient()

        secret_path = self.client.secret_version_path(self.project_id,
                                                      self.secret_name,
                                                      self.version)
        response = self.client.access_secret_version(secret_path)
        return response.payload.data.decode('UTF-8')
