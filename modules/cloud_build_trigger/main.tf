resource "google_cloudbuild_trigger" "filename-trigger" {
  provider = google-beta
  github {
    name = var.repo
    push {
      branch = var.branch
    }
  }

  substitutions = {
    _IMAGE_NAME = var.image_name
  }

  filename = "cloudbuild.yaml"
}