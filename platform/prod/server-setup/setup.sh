#!/bin/bash

SCRIPT_DIR="$(dirname "$(realpath "$0")")"

# Detect wall number from hostname
WALL=$(hostname | sed -e 's/.*\(wall[1-2]\).ilabt.iminds.be$/\1/')

# Execute scripts
bash "$SCRIPT_DIR/enable-nat.sh"

bash "$SCRIPT_DIR/configure-public-ip.sh"

bash "$SCRIPT_DIR/extend-partition.sh"
bash "$SCRIPT_DIR/upgrade-packages.sh"
bash "$SCRIPT_DIR/configure-firewall.sh"
bash "$SCRIPT_DIR/enforce-password-on-sudo.sh"
bash "$SCRIPT_DIR/non-experiment-setup.sh"
