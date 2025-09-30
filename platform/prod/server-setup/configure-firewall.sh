#!/bin/bash

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (default port 22)
sudo ufw allow 22/tcp

# Allow HTTP (port 80) and HTTPS (port 443)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow Kubernetes API port (6443)
sudo ufw allow 6443/tcp

# Reload UFW
sudo ufw reload

sudo ufw --force enable
