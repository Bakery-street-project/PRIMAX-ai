variable "project" {
  description = "GCP Project ID"
  type        = string
  default     = "mythicnode"
}

variable "region" {
  default = "us-central1"
}

variable "zone" {
  default = "us-central1-c"
}

variable "vm_count" {
  default = 2
}
