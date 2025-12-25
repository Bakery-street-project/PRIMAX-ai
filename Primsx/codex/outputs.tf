output "instance_ips" {
  description = "Public IPs of all instances"
  value       = [for i in google_compute_instance.my-vm : i.network_interface[0].access_config[0].nat_ip]
}

output "instance_names" {
  value = [for i in google_compute_instance.my-vm : i.name]
}
