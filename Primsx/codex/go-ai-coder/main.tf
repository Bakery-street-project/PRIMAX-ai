terraform {
  required_providers {
    google = { source="hashicorp/google", version="~>4.0" }
  }
  backend "gcs" {
    bucket = "my-gcp-tfstate-bucket"
    prefix = "go-ai-coder"
  }
}

provider "google" {
  project = var.gcp_project
  region  = var.gcp_region
}

variable "gcp_project" {}
variable "gcp_region" {}

resource "random_id" "bucket_id" { byte_length = 4 }
resource "google_storage_bucket" "demo" {
  name     = "demo-bucket-${random_id.bucket_id.hex}"
  location = var.gcp_region
}
