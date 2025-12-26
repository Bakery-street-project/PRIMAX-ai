provider "google" {
  project = var.project
  region  = var.region
}

resource "google_compute_instance" "my-vm" {
  count        = var.vm_count
  name         = "bakery-vm-${count.index + 1}"
  machine_type = "e2-medium"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-2204-jammy-v20240118"
    }
  }

  network_interface {
    network = var.network_config
    access_config {}
  }

  tags = ["bakery-agent", "http-server"]
}
