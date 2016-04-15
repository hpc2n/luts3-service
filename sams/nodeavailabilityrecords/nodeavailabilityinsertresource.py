# -*- coding: utf-8 -*-
"""
Insertion resources for SGAS.

Used for inserting node availability records into database.

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
from sams.nodeavailabilityrecords import arsplitter, arparser, arconverter

ACTION_NODE_AVAILABILITY_INSERT   = 'nodeavailabilityinsert'
CTX_NODE_AVAILABILITY_SYSTEM  = 'nodeavailability_machine'

class NodeAvailabilityInsertChecker(ctxinsertchecker.InsertChecker):

    CONTEXT_KEY = CTX_NODE_AVAILABILITY_SYSTEM

class NodeAvailabilityRecordInsertResource(GenericInsertResource):
    
    PLUGIN_ID   = 'ar'
    PLUGIN_NAME = 'NodeAvailabiliyRegistration'     

    authz_right = ACTION_NODE_AVAILABILITY_INSERT
    insert_error_msg = 'Error during node availabiliy insert: %s'
    insert_authz_reject_msg = 'Rejecting nodea vailabiliy insert for %s. No insert rights.'
    
    def __init__(self, cfg, db, authorizer):
        GenericInsertResource.__init__(self,db,authorizer)
        authorizer.addChecker(self.authz_right, NodeAvailabilityInsertChecker(authorizer.insert_check_depth))
        authorizer.rights.addActions(ACTION_NODE_AVAILABILITY_INSERT)
        authorizer.rights.addOptions(ACTION_NODE_AVAILABILITY_INSERT,[ rights.OPTION_ALL ])
        authorizer.rights.addContexts(ACTION_NODE_AVAILABILITY_INSERT,[ CTX_NODE_AVAILABILITY_SYSTEM ])

    def insertRecords(self, data, subject, hostname):
        return self._insertNodeAvailabilityRecords(data, self.db, self.authorizer, subject, hostname)

    def _insertNodeAvailabilityRecords(self, node_availability_record_data, db, authorizer, insert_identity=None, insert_hostname=None):
        
        insert_time = time.gmtime()

        ar_docs = []

        for ar_element in arsplitter.splitCLDocument(node_availability_record_data):
            ar_doc = arparser.xmlToDict(ar_element,
                                    insert_identity=insert_identity,
                                    insert_hostname=insert_hostname,
                                    insert_time=insert_time)
            ar_docs.append(ar_doc)

        machine_names = set( [ doc.get('machine_name') for doc in ar_docs ] )
        ctx = [ ('machine_name', ss) for ss in site ]

        if authorizer.isAllowed(insert_identity, ACTION_NODE_AVAILABILITY_INSERT, ctx):
            return self.insertNodeAvailabilityRecords(db, ar_docs)
        else:
            MSG = 'Subject %s is not allowed to perform insertion for node availability machine: %s' % (insert_identity, ','.join(machine_names))
            return defer.fail(dberror.SecurityError(MSG))
        
        
    def insertNodeAvailabilityRecords(self, db, node_availability_record_docs, retry=False):
        
        arg_list = arconverter.createInsertArguments(node_availability_record_docs)

        return db.recordInserter('node availability', 'ar_node_availability_record', arg_list)
