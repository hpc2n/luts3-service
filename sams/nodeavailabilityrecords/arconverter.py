# -*- coding: utf-8 -*-
"""
Parser for converting nodeavailability records into statements for inserting data into
PostgreSQL.

Author: Magnus Jonsson
Copyright: HPC2N, Umeå Universitet
"""

from twisted.python import log

ARG_LIST = [
    'record_id',
    'create_time',
    'site',
    'machine_name',
    'start_time',
    'end_time',
    'available',
    'unavailable',
    'reserved',
    'unknown',
    'insert_host',
    'insert_identity',
    'insert_time'
]

def createInsertArguments(node_availabiliyrecord_docs, insert_identity=None, insert_hostname=None):

    args = []

    for ar_doc in node_availabiliyrecord_docs:
        arg = [ ar_doc.get(a, None) for a in ARG_LIST ]
        args.append(arg)

    return args

