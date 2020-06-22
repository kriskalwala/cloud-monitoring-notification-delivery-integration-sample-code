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

import secrets

"""Flask config."""

class Config:
    """Base config."""

    FLASK_ENV = 'production'
    TESTING = False
    DEBUG = False



class ProdConfig(Config):

    def __init__(self):
        self._philips_hue_ip = None
        self._philips_hue_username = None


    @property
    def PHILIPS_HUE_IP(self):
        if self._philips_hue_ip is None:
            secret = secrets.GoogleSecretManagerSecret(
                'alertmanager-2020-intern-r', 'philips_ip')
            self._philips_hue_ip = secret.get_secret_value()

        return self._philips_hue_ip


    @property
    def PHILIPS_HUE_USERNAME(self):
        if self._philips_hue_username is None:
            secret = secrets.GoogleSecretManagerSecret(
                'alertmanager-2020-intern-r', 'philips_username')
            self._philips_hue_username = secret.get_secret_value()

        return self._philips_hue_username



class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True

    def __init__(self):
        self._philips_hue_ip = None
        self._philips_hue_username = None


    @property
    def PHILIPS_HUE_IP(self):
        if self._philips_hue_ip is None:
            secret = secrets.EnvironmentVariableSecret('PHILIPS_HUE_IP')
            self._philips_hue_ip = secret.get_secret_value()

        return self._philips_hue_ip


    @property
    def PHILIPS_HUE_USERNAME(self):
        if self._philips_hue_username is None:
            secret = secrets.EnvironmentVariableSecret('PHILIPS_HUE_USERNAME')
            self._philips_hue_username = secret.get_secret_value()

        return self._philips_hue_username



configs = {
    'prod': ProdConfig,
    'dev': DevConfig,
    'default': ProdConfig
}
