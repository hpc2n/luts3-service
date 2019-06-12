# -*- coding: utf-8 -*-
"""
Insertion resources for SGAS.

Used for inserting software accounting records into database.

Author: Magnus Jonsson
Copyright: HPC2N, Umeå Universitet
"""
from twisted.internet import defer
from twisted.python import log
from twisted.enterprise import adbapi

import time

import psycopg2
import psycopg2.extensions # not used, but enables tuple adaption

from sgas.authz import rights, ctxinsertchecker
from sgas.generic.insertresource import GenericInsertResource
from sgas.database import error as dberror
from sams.softwareaccountingrecords import splitter, parser, converter

ACTION_SOFTWARE_ACCOUNTING_INSERT   = 'softwareaccountinginsert'
CTX_SOFTWARE_ACCOUNTING_SYSTEM  = 'softwareaccounting_machine'

class SoftwareAccountingInsertChecker(ctxinsertchecker.InsertChecker):

    CONTEXT_KEY = CTX_SOFTWARE_ACCOUNTING_SYSTEM

class SoftwareAccountingRecordInsertResource(GenericInsertResource):
    
    PLUGIN_ID   = 'sa'
    PLUGIN_NAME = 'SoftwareAccountingRegistration'     

    authz_right = ACTION_SOFTWARE_ACCOUNTING_INSERT
    insert_error_msg = 'Error during software accounting insert: %s'
    insert_authz_reject_msg = 'Rejecting software accounting insert for %s. No insert rights.'
    
    def __init__(self, cfg, db, authorizer):
        GenericInsertResource.__init__(self,db,authorizer)
        authorizer.addChecker(self.authz_right, SoftwareAccountingInsertChecker(authorizer.insert_check_depth))
        authorizer.rights.addActions(ACTION_SOFTWARE_ACCOUNTING_INSERT)
        authorizer.rights.addOptions(ACTION_SOFTWARE_ACCOUNTING_INSERT,[ rights.OPTION_ALL ])
        authorizer.rights.addContexts(ACTION_SOFTWARE_ACCOUNTING_INSERT,[ CTX_SOFTWARE_ACCOUNTING_SYSTEM ])

    def insertRecords(self, data, subject, hostname):
        return self._insertSoftwareAccountingRecords(data, self.db, self.authorizer, subject, hostname)

    def _insertSoftwareAccountingRecords(self, software_accounting_record_data, db, authorizer, insert_identity=None, insert_hostname=None):
        
        insert_time = time.gmtime()

        docs = []

        for element in splitter.splitDocument(software_accounting_record_data):
            doc = parser.xmlToDict(element,
                                    insert_identity=insert_identity,
                                    insert_hostname=insert_hostname,
                                    insert_time=insert_time)
            docs.append(doc)

        machine_names = set( [ doc.get('machine_name') for doc in docs ] )
        ctx = [ ('machine_name', ss) for ss in machine_names ]

        if authorizer.isAllowed(insert_identity, ACTION_SOFTWARE_ACCOUNTING_INSERT, ctx):
            return self.insertSoftwareAccountingRecords(db, docs)
        else:
            MSG = 'Subject %s is not allowed to perform insertion for software accounting machine: %s' % (insert_identity, ','.join(machine_names))
            return defer.fail(dberror.SecurityError(MSG))
        
        
    def insertSoftwareAccountingRecords(self, db, software_accounting_record_docs, retry=False):
        
        arg_list = converter.createInsertArguments(software_accounting_record_docs)

        return db.recordInserter('software accounting', 'software_accounting_record', arg_list)

