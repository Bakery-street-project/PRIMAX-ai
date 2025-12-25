terraform {
  # backend "gcs" {
  #   bucket = "PUT_BUCKET_HERE"
  #   prefix = "go-ai-superbrain"
  # }
  backend "local" {
    path = "terraform.tfstate"
  }
}
# ... (rest of your Terraform config as above)
