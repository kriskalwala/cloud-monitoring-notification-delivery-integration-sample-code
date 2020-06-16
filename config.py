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

load_dotenv()


class Config:
    """Base config."""

    FLASK_ENV = 'production'
    TESTING = False
    DEBUG = False
    
    PHILIPS_HUE_URL = os.environ.get('PHILIPS_URL')
    LIGHT_ID = 1
    
    
class ProdConfig(Config):
    pass


class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    

configs = {
    'prod': ProdConfig,
    'dev': DevConfig,
    'default': ProdConfig
}