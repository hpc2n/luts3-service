"""
Insertion resources for SGAS.

Used for inserting cloud records into database.

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
from sams.cloudrecords import clsplitter, clparser, clconverter

ACTION_CLOUD_INSERT   = 'cloudinsert'
CTX_CLOUD_SYSTEM  = 'cloud_system'

class CloudInsertChecker(ctxinsertchecker.InsertChecker):

    CONTEXT_KEY = CTX_CLOUD_SYSTEM

class CloudUsageRecordInsertResource(GenericInsertResource):
    
    PLUGIN_ID   = 'cr'
    PLUGIN_NAME = 'CloudRegistration'     

    authz_right = ACTION_CLOUD_INSERT
    insert_error_msg = 'Error during cloud usage insert: %s'
    insert_authz_reject_msg = 'Rejecting cloud usage insert for %s. No insert rights.'
    
    def __init__(self, cfg, db, authorizer):
        GenericInsertResource.__init__(self,db,authorizer)
        authorizer.addChecker(self.authz_right, CloudInsertChecker(authorizer.insert_check_depth))
        authorizer.rights.addActions(ACTION_CLOUD_INSERT)
        authorizer.rights.addOptions(ACTION_CLOUD_INSERT,[ rights.OPTION_ALL ])
        authorizer.rights.addContexts(ACTION_CLOUD_INSERT,[ CTX_CLOUD_SYSTEM ])

    def insertRecords(self, data, subject, hostname):
        return self._insertCloudUsageRecords(data, self.db, self.authorizer, subject, hostname)

    def _insertCloudUsageRecords(self, cloudrecord_data, db, authorizer, insert_identity=None, insert_hostname=None):
        
        insert_time = time.gmtime()

        cl_docs = []

        for cl_element in clsplitter.splitCLDocument(cloudrecord_data):
            cl_doc = clparser.xmlToDict(cl_element,
                                    insert_identity=insert_identity,
                                    insert_hostname=insert_hostname,
                                    insert_time=insert_time)
            cl_docs.append(cl_doc)

        resource = set( [ doc.get('resource') for doc in cl_docs ] )
        ctx = [ ('resource', ss) for ss in resource ]

        if authorizer.isAllowed(insert_identity, ACTION_CLOUD_INSERT, ctx):
            return self.insertCloudUsageRecords(db, cl_docs)
        else:
            MSG = 'Subject %s is not allowed to perform insertion for cloud systems: %s' % (insert_identity, ','.join(resource))
            return defer.fail(dberror.SecurityError(MSG))
        
        
    def insertCloudUsageRecords(self, db, cloudrecord_docs, retry=False):
        
        arg_list = clconverter.createInsertArguments(cloudrecord_docs)

        return db.recordInserter('cloud usage', 'cr_create_record', arg_list)
