terraform {
  backend "gcs" {
    bucket = "my-gcp-tfstate-bucket"
    prefix = "go-ai-coder"
  }
}
provider "google" {}
