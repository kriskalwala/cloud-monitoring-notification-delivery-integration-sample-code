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
from google.cloud import secretmanager

load_dotenv()


class Config:
    """Base config."""

    FLASK_ENV = 'production'
    TESTING = False
    DEBUG = False



class ProdConfig(Config):
    def __init__(self):
        self.__philips_hue_ip = None
        self.__philips_hue_username = None


    @property
    def PHILIPS_HUE_IP(self):
        if self.__philips_hue_ip is None:
            client = secretmanager.SecretManagerServiceClient()
            secret_path = client.secret_version_path('alertmanager-2020-intern-r',
                                                     'philips_ip', 'latest')
            response = client.access_secret_version(secret_path)
            self.__philips_hue_ip = response.payload.data.decode('UTF-8')

        return self.__philips_hue_ip


    @property
    def PHILIPS_HUE_USERNAME(self):
        if self.__philips_hue_username is None:
            client = secretmanager.SecretManagerServiceClient()
            secret_path = client.secret_version_path('alertmanager-2020-intern-r',
                                                     'philips_username', 'latest')
            response = client.access_secret_version(secret_path)
            self.__philips_hue_username = response.payload.data.decode('UTF-8')

        return self.__philips_hue_username



class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    PHILIPS_HUE_URL = os.environ.get('PHILIPS_URL')



configs = {
    'prod': ProdConfig,
    'dev': DevConfig,
    'default': ProdConfig
}
