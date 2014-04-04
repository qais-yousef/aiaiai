#!/bin/sh
#
# Copyright 2014 Intel Corporation
# Author: Jacob Keller
# License: GPLv2

service=$1
email=$2

(
echo "$service has crashed, and you need to restart it!"
echo "Here is the systemctl status output:"
systemctl status -n 100 "$service"
) | mutt -s "$service crashed!" $email
