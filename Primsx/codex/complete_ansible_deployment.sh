#!/bin/bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - COMPLETE_ANSIBLE_DEPLOYMENT.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

set -e

echo "=== Step 1: Verify Ansible Inventory ==="
cat ansible/hosts.yml

echo -e "\n=== Step 2: Create Missing Ansible Playbooks ==="
cat <<'SITE' > ansible/site.yml
- name: Configure all VMs with agents and tools
  hosts: all
  become: yes
  tasks:
    - name: Update apt cache
      apt:
        update_cache: yes
        cache_valid_time: 3600

    - name: Install base packages
      apt:
        name:
          - python3-pip
          - python3-venv
          - git
          - docker.io
          - npm
          - tmux
          - jq
          - build-essential
          - curl
          - wget

    - name: Install Go
      shell: |
        wget https://go.dev/dl/go1.23.0.linux-amd64.tar.gz
        tar -C /usr/local -xzf go1.23.0.linux-amd64.tar.gz
        echo 'export PATH=$PATH:/usr/local/go/bin' >> /etc/profile
      args:
        creates: /usr/local/go/bin/go

    - name: Clone agent repositories
      git:
        repo: "https://github.com/Bakery-street-project/{{ item }}.git"
        dest: "/opt/{{ item }}"
        version: main
      loop:
        - agentic-experiments
        - go-ai-coder
        - monitoring-dashboard

    - name: Setup Python agents
      shell: |
        cd /opt/agentic-experiments
        python3 -m venv .venv
        source .venv/bin/activate
        [ -f requirements.txt ] && pip install -r requirements.txt || true

    - name: Setup Go agents
      shell: |
        cd /opt/go-ai-coder
        export PATH=$PATH:/usr/local/go/bin
        go mod download
        go build -o bin/go-ai-coder cmd/main.go
      environment:
        PATH: "/usr/local/go/bin:{{ ansible_env.PATH }}"

    - name: Copy neuromorphic brain script
      copy:
        src: ../brain_perplexity_research.py
        dest: /opt/brain_perplexity_research.py
        mode: '0755'

    - name: Setup systemd agent timer
      copy:
        dest: /etc/systemd/system/agent-update.service
        content: |
          [Unit]
          Description=Agentic Brain Update

          [Service]
          Type=oneshot
          ExecStart=/usr/bin/python3 /opt/brain_perplexity_research.py

    - name: Setup systemd timer
      copy:
        dest: /etc/systemd/system/agent-update.timer
        content: |
          [Unit]
          Description=Hourly Agentic Brain Update

          [Timer]
          OnCalendar=hourly
          Unit=agent-update.service

          [Install]
          WantedBy=timers.target

    - name: Enable and start timer
      systemd:
        name: agent-update.timer
        enabled: yes
        state: started
        daemon_reload: yes
SITE

echo "=== Step 3: Run Ansible Playbook ==="
ansible-playbook -i ansible/hosts.yml ansible/site.yml

echo "=== Ansible deployment complete! ==="
