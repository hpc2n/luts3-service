"""
Parser for converting cloud records into statements for inserting data into
PostgreSQL.

Author: Magnus Jonsson
Copyright: HPC2N, Umeå Universitet
"""

from twisted.python import log

from sams.cloudrecords import clelements as cl

ARG_LIST = [
    'record_id',
    'create_time',
    'site',
    'project',
    'username',
    'instance',
    'start_time',
    'end_time',
    'duration',
    'region',
    'zone',
    'flavour',
    'cost',
    'allocated_cpu',
    'allocated_disk',
    'allocated_memory',
    'used_cpu',
    'used_disk',
    'used_memory',
    'used_network_up',
    'used_network_down',
    'iops',
    'storage_type',
    'file_count',
    'insert_host',
    'insert_identity',
    'insert_time'
]

def createInsertArguments(cloudrecord_docs, insert_identity=None, insert_hostname=None):

    args = []

    for sr_doc in cloudrecord_docs:
        log.msg(sr_doc);
        arg = [ sr_doc.get(a, None) for a in ARG_LIST ]
        if sr_doc.get('record_type') == cl.CLOUD_COMPUTE_RECORD:
            args.append(['cr_create_compute_record'] + arg)
        elif sr_doc.get('record_type') == cl.CLOUD_STORAGE_RECORD:
            args.append(['cr_create_storage_record'] + arg)
        else:
            log.msg("record_type is missing or wrong in record: %s" % sr_doc.get('record_type','missing :-('), system='sams.CloudRecods')

    return args

