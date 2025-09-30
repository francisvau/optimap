#!/bin/bash

sudo apt update

echo 'grub-pc grub-pc/install_devices multiselect /dev/sda' | sudo debconf-set-selections
echo 'grub-pc grub-pc/timeout string 5' | sudo debconf-set-selections
echo 'grub-pc grub2/update_nvram boolean true' | sudo debconf-set-selections

sudo DEBIAN_FRONTEND=noninteractive apt -y dist-upgrade
sudo apt -y autoremove
