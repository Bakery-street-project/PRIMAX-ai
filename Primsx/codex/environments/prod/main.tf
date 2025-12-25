terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket         = "my-tf-state-bucket"
    key            = "envs/${terraform.workspace}/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "tf-state-lock"
  }
}

provider "aws" {
  region = "us-west-2"
}

