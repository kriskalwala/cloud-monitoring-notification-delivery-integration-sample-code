![](https://github.com/googleinterns/cloud-monitoring-notification-delivery-integration-sample-code/workflows/Continuous%20Integration/badge.svg)

# Sample Code for the Cloud Monitoring Notification Delivery Integration Guide

**This is not an officially supported Google product.**

Complete sample code to accompany the Google Cloud Monitoring Notification
Delivery Integration solutions guide.

This repository provides an example of how a Google Cloud user can forward
**[notifications](https://cloud.google.com/monitoring/alerts#how_does_alerting_work)**
to third-party integrations not officially supported at
**[notification options](https://cloud.google.com/monitoring/support/notification-options)**.

## Source Code Headers

Every file containing source code must include copyright and license
information. This includes any JS/CSS files that you might be serving out to
browsers. (This is to help well-intentioned people avoid accidental copying that
doesn't comply with the license.)

Apache header:

    Copyright 2020 Google LLC

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        https://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
    
## Terraform Setup

Terraform configurations are used to create the infrastructure needed for this integration, such as Pub/Sub topics and subscriptions, alerting policies, custom metrics, and Cloud Run instances. The `dev` and `prod` environments each have their own Terraform configurations, which can be found in the ```environments/``` directory. Terraform modules can be found in the ```modules/``` directory.

Deployment with Terraform will be automated through source code changes in GitHub. To test the deployment manually, navigate to the desired environment folder (`environments/dev` or `environments/prod`) and run the following:

Initialize a working directory containing Terraform configuration files:
```
terraform init
```
Optional; useful if you want to see what changes will be made without applying them yet:
```
terraform plan
``` 
Apply configuration changes:
```
terraform apply
```
Information about the created resources should appear in the output.
