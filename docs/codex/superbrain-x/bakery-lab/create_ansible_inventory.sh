#!/bin/bash
IPS=$(terraform output -json | jq -r '.instance_ips.value[]')
cat > ansible/hosts.yml <<HOSTS
all:
  hosts:
HOSTS
i=1
for ip in $IPS; do
  echo "    vm-$i: { ansible_host: $ip }" >> ansible/hosts.yml
  ((i++))
done
