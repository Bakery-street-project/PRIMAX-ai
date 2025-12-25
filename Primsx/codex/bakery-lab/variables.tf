variable "project" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  default     = "us-central1"
}

variable "zone" {
  description = "GCP Zone"
  default     = "us-central1-c"
}

variable "network_config" {
  description = "Network for VMs"
  default     = "default"
}

variable "vm_count" {
  description = "Number of VMs to create"
  default     = 3
}
