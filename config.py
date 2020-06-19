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

    PHILIPS_HUE_IP = secrets.GoogleSecretManagerSecret(
        'alertmanager-2020-intern-r', 'philips_ip')
    PHILIPS_HUE_USERNAME = secrets.GoogleSecretManagerSecret(
        'alertmanager-2020-intern-r', 'philips_username')

    def __init__(self):
        self.PHILIPS_HUE_IP = self.PHILIPS_HUE_IP.get_secret_value()
        self.PHILIPS_HUE_USERNAME = self.PHILIPS_HUE_USERNAME.get_secret_value()



class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    PHILIPS_HUE_IP = secrets.EnvironmentVariableSecret('PHILIPS_HUE_IP')
    PHILIPS_HUE_USERNAME = secrets.EnvironmentVariableSecret('PHILIPS_HUE_USERNAME')

    def __init__(self):
        self.PHILIPS_HUE_IP = self.PHILIPS_HUE_IP.get_secret_value()
        self.PHILIPS_HUE_USERNAME = self.PHILIPS_HUE_USERNAME.get_secret_value()



configs = {
    'prod': ProdConfig,
    'dev': DevConfig,
    'default': ProdConfig
}
