#!/bin/bash

sudo mkdir -p /etc/registry

echo "Set password for registry admin"
sudo htpasswd -Bc /etc/registry/htpasswd admin
