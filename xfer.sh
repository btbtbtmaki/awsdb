#!/bin/sh
if [ $# -ne 2 ]
then
  echo "Must specify IP address and KEY file path"
  exit 1
fi

# KEY_FILE=$2

scp -i $2 *.py ubuntu@$1:/home/ubuntu
