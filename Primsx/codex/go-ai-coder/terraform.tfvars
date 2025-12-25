vm_count       = 5
cloud_provider = "gcp"
network_config = "default"
firewall_rules = ["80/tcp", "443/tcp", "3000/tcp"]
project        = "<YOUR_GCP_PROJECT>"
zone           = "<YOUR_GCP_ZONE>"
credentials    = "<PATH_TO_GCP_SERVICE_ACCOUNT_JSON>"
