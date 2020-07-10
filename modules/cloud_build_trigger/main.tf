resource "google_cloudbuild_trigger" "filename-trigger" {
  trigger_template {
    branch_name = var.branch
    repo_name   = var.repo
  }

  substitutions = {
    _IMAGE_NAME = var.image_name
  }

  filename = "cloudbuild.yaml"
}