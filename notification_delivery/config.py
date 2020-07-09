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

"""Flask config."""

import os
from dotenv import load_dotenv
from notification_delivery import secrets

load_dotenv()

class Config:
    """Base config."""

    FLASK_ENV = 'production'
    LOGGING_LEVEL = 'INFO'
    TESTING = False
    DEBUG = False
    LIGHT_ID = '1'

    # Mappings between Google Cloud alerting policy names
    # and HSB color system hue values between 0 and 65535.
    # Each mapping indicates what hues the light bulb should
    # light up when receiving a notification about an
    # "open" or "closed" incident regarding a specific
    # policy. The default mapping indicates the hues
    # it should light up for notifications about "open"
    # or "closed" incidents regarding any other unspecified
    # policy.
    POLICY_HUE_MAPPING = {
        'policyA': {
            'open': 5620, # orange
            'closed': 42237  # blue
        },
        'policyB': {
            'open': 10126,  # yellow
            'closed': 48013  # purple
        },
        'default': {
            'open': 65280,  # red
            'closed': 24432  # green
        }
    }



class ProdConfig(Config):
    """Production config."""

    def __init__(self):
        self._philips_hue_ip = None
        self._philips_hue_username = None


    @property
    def BRIDGE_IP_ADDRESS(self):
        if self._philips_hue_ip is None:
            secret = secrets.GoogleSecretManagerSecret(
                'alertmanager-2020-intern-r', 'philips_ip')
            self._philips_hue_ip = secret.get_secret_value()

        return self._philips_hue_ip


    @property
    def USERNAME(self):
        if self._philips_hue_username is None:
            secret = secrets.GoogleSecretManagerSecret(
                'alertmanager-2020-intern-r', 'philips_username')
            self._philips_hue_username = secret.get_secret_value()

        return self._philips_hue_username



class DevConfig(Config):
    """Development config."""

    FLASK_ENV = 'development'
    LOGGING_LEVEL = 'DEBUG'
    DEBUG = True
    TESTING = True


    def __init__(self):
        self._philips_hue_ip = None
        self._philips_hue_username = None


    @property
    def BRIDGE_IP_ADDRESS(self):
        if self._philips_hue_ip is None:
            secret = secrets.EnvironmentVariableSecret('PHILIPS_HUE_IP')
            self._philips_hue_ip = secret.get_secret_value()

        return self._philips_hue_ip


    @property
    def USERNAME(self):
        if self._philips_hue_username is None:
            secret = secrets.EnvironmentVariableSecret('PHILIPS_HUE_USERNAME')
            self._philips_hue_username = secret.get_secret_value()

        return self._philips_hue_username



class TestConfig(Config):
    """Test config."""

    FLASK_ENV = 'test'
    LOGGING_LEVEL = 'DEBUG'
    DEBUG = True
    TESTING = True

    BRIDGE_IP_ADDRESS = '127.0.0.1'
    USERNAME = 'test-user'

    # Overide this mapping to ensure unit tests
    # in main_test.py always use the same mapping even
    # if the mapping in the base Config is modified.
    # This is important since the tests are based of /
    # assume the values in this specific mapping.
    POLICY_HUE_MAPPING = {
        'policyA': {
            'open': 5620,
            'closed': 42237
        },
        'policyB': {
            'open': 10126,
            'closed': 48013
        },
        'default': {
            'open': 65280,
            'closed': 24432
        }
    }


_ENVIRONMENT_TO_CONFIG_MAPPING = {
    'prod': ProdConfig,
    'dev': DevConfig,
    'test': TestConfig,
    'default': ProdConfig
}



def load():
    environment_name = os.environ.get('FLASK_APP_ENV', 'default')
    return _ENVIRONMENT_TO_CONFIG_MAPPING[environment_name]()
