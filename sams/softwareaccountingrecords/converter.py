# -*- coding: utf-8 -*-
"""
Parser for converting software accounting records into statements for inserting data into
PostgreSQL.

Author: Magnus Jonsson
Copyright: HPC2N, Umeå Universitet
"""

from twisted.python import log

from psycopg2.extensions import adapt, AsIs

ARG_LIST = [
    'record_id',
    'create_time',
    'record_id',
    'softwares',
    'insert_host',
    'insert_identity',
    'insert_time'
]

def createInsertArguments(software_accounting_record_docs, insert_identity=None, insert_hostname=None):

    args = []

    for doc in software_accounting_record_docs:
        arg = []
        for a in ARG_LIST:
            # Handle softwares
            if a == 'softwares':
                softwares = []
                software = doc.get(a, None)
                for sw in software:
                        softwares.append(AsIs("ROW(%s::text,%s::text,%s::text,%s::boolean,%s::real)::software_accounting_software" %
                            (adapt(sw['name']),adapt(sw['version']),adapt(sw['local_version']),
                                adapt(sw['user_provided']) ,adapt(sw['usage'])))
                            )
                arg.append(softwares)
            else:
                arg.append(doc.get(a, None))
        args.append(arg)

    return args
