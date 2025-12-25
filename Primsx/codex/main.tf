provider "google" {
  project = var.project
  region  = var.region
}

resource "google_compute_instance" "my-vm" {
  count        = var.vm_count
  name         = "bakery-vm-${count.index + 1}"
  machine_type = "e2-micro"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }

  tags = ["bakery-agent", "http-server"]
}
