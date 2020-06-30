# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


locals {
  "env" = "dev"
}

provider "google" {
  project = "${var.project}"
}

module "pubsub" {
  source  = "terraform-google-modules/pubsub/google"
  version = "~> 1.3"
  
  topic              = "tf-topic"
  project_id         = "${var.project}"
  push_subscriptions = [
    {
      name              = "alert-push-subscription"
      push_endpoint     = "https://pubsub-tutorial-uvbet5mdya-uw.a.run.app/"
    }
  ]
}

#module "service_accounts" {
#  source        = "terraform-google-modules/service-accounts/google"
#  version       = "~> 2.0"
#  project_id    = "${var.project}"
#  prefix        = "test-sa"
#  names         = ["first", "second"]
#  project_roles = [
#    "project-foo=>roles/viewer",
#    "project-spam=>roles/storage.objectViewer",
#  ]
#}

#module "firewall" {
#  source  = "../../modules/firewall"
#  project = "${var.project}"
#  subnet  = "${module.vpc.subnet}"
#}