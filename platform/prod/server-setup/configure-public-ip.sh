#!/bin/bash

PUBLIC_IP="193.190.127.177"
CONTROL_INTERFACE="enp1s0f0"
modprobe 8021q
vconfig add "$CONTROL_INTERFACE" 28
ifconfig "$CONTROL_INTERFACE".28 "$PUBLIC_IP" netmask 255.255.255.192
route del default ; route add default gw 193.190.127.129
