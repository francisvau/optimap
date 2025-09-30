#!/bin/bash

echo "y" | sudo bash -e -c '. <(wget -O - -q https://gitlab.ilabt.imec.be/wvdemeer/wall-public-scripts/-/raw/master/expand-root-disk.sh)'
