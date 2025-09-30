#!/bin/bash

FILE="/etc/sudoers.d/99-emulab"

# Set password for the current user
sudo passwd $(whoami)

# Backup the original file
sudo cp "$FILE" "$FILE.bak"

# Remove 'NOPASSWD:' from the file
sudo sed -i 's/NOPASSWD://g' "$FILE"

# Verify syntax using visudo
sudo visudo -c -f "$FILE"

if [ $? -eq 0 ]; then
    echo "Successfully removed NOPASSWD. Password is now required for sudo."
else
    echo "Error: sudoers file syntax issue. Restoring backup."
    sudo cp "$FILE.bak" "$FILE"
fi
