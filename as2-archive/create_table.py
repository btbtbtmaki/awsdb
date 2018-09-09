#!/usr/bin/env python

'''
   Create the table for the BasicDB exercise.

   You only execute this ONCE.
'''

import boto.dynamodb2

from boto.dynamodb2.table import Table
from boto.dynamodb2.fields import HashKey
from boto.dynamodb2.types import NUMBER

# Modify these as necessary
TABLE_NAME = "activities"
READ_CAPACITY = 1
WRITE_CAPACITY = 1

if __name__ == "__main__":
    acts = Table.create (
        TABLE_NAME,
        schema=[
            HashKey('id', data_type=NUMBER)
            ],
        throughput = {
                'read': READ_CAPACITY,
                'write': WRITE_CAPACITY
                },
        connection=boto.dynamodb2.connect_to_region('us-west-2')
)
