terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "6.17.0"
    }
  }
}


provider "google" {
  #configuration options
  project = "terraform-demo-435315"
  region  = "asia-southeast"
  zone    = "asia-southeast1-a"
}

resource "google_storage_bucket" "auto-expire" {
  name          = "terraform-demo-435315-gcsbucket"
  location      = "ASIA"
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 3
    }
    action {
      type = "Delete"
    }
  }

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}


