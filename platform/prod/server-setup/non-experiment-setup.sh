#!/bin/bash

SCRIPT_DIR="$(dirname "$(realpath "$0")")"

bash "$SCRIPT_DIR/install-custom-dependencies.sh"
bash "$SCRIPT_DIR/registry-admin-setup.sh"


# Install kube-state-metrics using helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install kube-state-metrics prometheus-community/kube-state-metrics -n monitoring
