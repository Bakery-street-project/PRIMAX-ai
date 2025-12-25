terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  backend "gcs" {
    bucket = "my-gcp-tfstate-bucket"
    prefix = "go-ai-superbrain"
  }
}

provider "google" {
  project = var.project
  region  = var.region
}

variable "project" {}
variable "region" {}

resource "google_cloud_run_service" "svc" {
  name     = "go-ai-superbrain"
  location = var.region
  template {
    spec {
      containers {
        image = "gcr.io/${var.project}/go-ai-superbrain:latest"
        ports {
          container_port = 8080
        }
      }
    }
  }
}
