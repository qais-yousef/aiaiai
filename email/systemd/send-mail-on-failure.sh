#!/bin/sh
#
# Copyright 2014 Intel Corporation
# Author: Jacob Keller
# License: GPLv2

(
echo "$1 has crashed, and you need to restart it!"
echo "Here is the systemctl status output:"
systemctl status -n 100 "$1"
) | mutt -s "$1 crashed!" jacob.e.keller@intel.com
