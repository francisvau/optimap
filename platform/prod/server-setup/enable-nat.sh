#!/bin/bash

wget -O - -nv --ciphers DEFAULT@SECLEVEL=1 https://www.wall2.ilabt.iminds.be/enable-nat.sh | sudo bash
