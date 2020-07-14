{% extends "_shared/templates/_tutorial_lesson.html" %}
{# DO NOT MODIFY THE PRECEDING LINE #}
{% block pagevariables %}
{# Set the title in the following line. This is required. #}
{% setvar title %}Delivering Cloud Monitoring Notifications to Third-Party Services using Pub/Sub, Terraform, and GitHub{% endsetvar %}

{# Prev/Next buttons. Default is no buttons. Enter filename to activate a button #}
{% setvar prev %}{% endsetvar %}
{% setvar next %}{% endsetvar %}

{# Set to 1 to show the cleanup block #}
{% setvar cleanup %}1{% endsetvar %}
{# Cleanup intro prompt is on by default. Set to 1 to hide the prompt. #}
{% setvar no_incurring_charges %}{% endsetvar %}

{# Set to 1 to show the whatsnext section.#}
{% setvar whatsnext %}1{% endsetvar %}

{# Change "template-basic" to your product's directory on the next line: #}
{% include "template-basic/_local_variables.html" %}
<meta name="book_path" value="{{book_path}}" />
<meta name="project_path" value="{{project_path}}" />
{% endblock %}

{% block overview %}

This tutorial is for GCP customers who want to deliver Cloud Monitoring alerts to third-party services that don’t have supported notification channels.

Follow this tutorial to write, deploy, and call a Cloud Run service from a Pub/Sub push subscription. The tutorial provides code samples of external integrations with Philips Hue smart light bulbs and Jira as destinations for alerts, which can easily be substituted with other services. Additionally, it explains steps for continuous integration using Cloud Build, Terraform, and GitHub.

This tutorial assumes you are familiar with Cloud Monitoring alerting and already have alerting policies in place.

{% endblock %}

{% block objectives %}

* Write a service to handle Pub/Sub messages and deliver them to a third-party service.
* Build and deploy the service to Cloud Run using Cloud Build, Terraform, and GitHub.


{% endblock %}

{% block costs %}

This is the `costs` block. It's required. If the tutorial incurs no costs,
simply state that the tutorial is free to run and briefly explain why.
Omitted after first page of multi-page tutorials.

This tutorial uses billable components of Google Cloud Platform, including:

* Cloud Build
* Cloud Storage
* Cloud Run
* Pub/Sub
* Secret Manager

Use the [pricing calculator](/products/calculator/){: target="_blank"} to
generate a cost estimate based on your projected usage.
{% dynamic if cloud.eligible_for_free_trial %}
New {{gcp_name_short}} users might be eligible for a
[free trial](/free/){: track-type="freeTrial" track-name="consoleLink" track-metadata-position="prerequisites" track-metadata-end-goal="signUp" target="_blank"}.
{% dynamic endif %}

{% endblock %}

{% block prerequisites %}

This is the `prerequisites` block. Use it to tell the user what software to
install or configure before they start the tutorial. Omitted after first page of
multi-page tutorials.

Note: Do not use this section to tell the user to set environment variables or
clone repositories. Instead, do that as the first section of the lesson
content section.

<ol>
{% dynamic include /docs/includes/___before_you_begin %}
</ol>

{% endblock %}

{% block lessoncontent %}

{# includes for cleanup and link to tutorials index page #}
{% include "solutions/_shared/_tutorial_index_link.html" %}
{% include "_shared/_delete_tutorial_resources.html" with name="tutorial doc type template" %}

This is the `lessoncontent` block. It has no default heading, so write some:

## Starting at H2

This is where you write your tutorial steps.

1. Write H2 headings as gerunds. For example, "Using headings."
1. Write numbered steps, and H3 and lower headings using imperative
   mood. For example, "Use subheadings."
1. Remember to use additional headings.

### Prepare the environment

If the reader has to clone a repository, run a script to initialize
environment variables, select a region and zone, or perform another task to
get ready for subsequent steps, include a **Preparing your {{gcp_name_short}}
working environment** section and include procedures for these tasks.

## Using additional headings to segment the work

Introduce the steps, provide some information about what's going on.

1. Do this.
1. Now do that.

### Use subheadings

If the steps get really long, say more than 5-7, consider breaking them up
into subsections. Use imperative mood in lower-level headings.

## Using the GitHub widget

The widget includes code from GitHub. It's the best way to show example code.

For example:

<pre>&#123;% include "cloud/_docwidgets/_github_include.html" with project="python-docs-samples"  file="appengine/standard/flask/hello_world/main.py" region_tag="app" %}</pre>

Which would render as:

{% include "cloud/_docwidgets/_github_include.html" with project="python-docs-samples"  file="appengine/standard/flask/hello_world/main.py" region_tag="app" %}

Be sure to explain what the code is doing and why.


{% endblock %}

{% block cleanup %}

This is the `cleanup` block. It's required if there are costs associated with
the tutorial. To hide the block, set the `cleanup` variable to empty at the top
of this file and delete this entire section.

In a multi-page tutorial, include this block on the final page.

The `cleanup` block includes an introductory sentence by default. To hide the
sentence, set the `no_incurring_charges` variable to `1` at the top of this
file.

You can use [the static includes](http://google3/googledata/devsite/site-cloud/en/_shared/_delete_tutorial_resources.html),
as shown here.

Note that if you use the `overview` variable, you must specify a string for the
tutorial name in a parameter to the include directive:

<pre>&#123;% include "_shared/_delete_tutorial_resources.html" with name="[YOUR_TUTORIAL_NAME]" %}</pre>

You should also set the `no_incurring_charges` variable to `1` in the header to
avoid having two introductions.

Here is the text for the `overview` variable:

{{overview}}

Other variables show up in the following sections. The headings are not part
of the variables.

### Deleting the project

{{console_delete_project}}

### Deleting instances

{{console_delete_gce_instances}}

### Deleting firewall rules for the default network

{{console_delete_firewall_rules_default}}

{% endblock %}

{% block whatsnext %}
This is the `whatsnext` block. It's required and should have at least the
link to the tutorial index page, as shown below. In a multi-page tutorial,
show this block only on the last page. To hide it, set the `whatsnext` variable
to empty at the top of this page.

*  Work through the tutorial.
*  Look through code samples.
*  {{tutorial_index_promo}}

{% endblock %}