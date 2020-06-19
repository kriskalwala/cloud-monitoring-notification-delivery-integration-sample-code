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

import os
from dotenv import load_dotenv
from google.cloud import secretmanager

load_dotenv()

class Secret:
    
    def get_secret():
        pass



class EnvironmentVariableSecret(Secret):
    
    def __init__(self, secret_name):
        self.secret_name = secret_name
    
    def get_secret():
        os.environ.get(self.secret_name)



class GoogleSecretManagerSecret(Secret):
    
    def __init__(self, project_id, secret_name, version="latest", client=None):
        self.project_id = project_id
        self.secret_name = secret_name
        self.version = version
        
        if client is not None:
            self.client = client
        else:
            self.client = secretmanager.SecretManagerServiceClient()


    def get_secret():
        secret_path = self.client.secret_version_path(self.project_id,
                                                      self.secret_name,
                                                      self.version)
        response = self.client.access_secret_version(secret_path)
        return response.payload.data.decode('UTF-8')
