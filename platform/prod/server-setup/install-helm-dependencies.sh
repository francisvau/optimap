#!/bin/bash

# install-helm-dependencies.sh

# Fail on errors
set -e

# Define namespace and values file
NAMESPACE="gitlab-runner"
VALUES_FILE="values.yaml"

# Add GitLab Helm repo if not added
if ! helm repo list | grep -q "gitlab"; then
    echo "Adding GitLab Helm repository"
    helm repo add gitlab https://charts.gitlab.io
    helm repo update gitlab
fi

# Install GitLab Runner using Helm
echo "Installing GitLab Runner using Helm"
helm upgrade --install gitlab-runner gitlab/gitlab-runner \
    --namespace "$NAMESPACE"  \
    --create-namespace \
    -f "$VALUES_FILE"

echo "GitLab Runner installation complete"
