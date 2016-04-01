"""
Wrapper for saving inserted storage records on file.

Author: Magnus Jonsson
Copyright: HPC2N, Umea Universitet, 2016
"""

from sgas.storagerecord.storageinsertresource import StorageUsageRecordInsertResource
from datetime import datetime

class StorageUsageRecordInsertResourceSave(StorageUsageRecordInsertResource):
    savepath = ""
    savecnt = 0

    def __init__(self, cfg, db, authorizer):
        StorageUsageRecordInsertResource.__init__(self,cfg,db,authorizer)
        self.savepath = cfg.get('StorageUsageRecordInsertResourceSave','savepath');

    # Save input storage record as file in 'savepath'
    def insertRecords(self, data, subject, hostname):
        try:
            self.savecnt += 1
            outputfile = "%s/sr.%s.%d.xml" % (self.savepath,
                    datetime.now().strftime("%Y%m%d%H%M%S"),self.savecnt)
            f = open(outputfile,"w")
            f.write(data)
            f.close()
        except IOError:
            log.msg('Failed to write file: %s' % outputfile,
                    system='sams.StorageUsageRecordInsertResourceSave')
            
        return StorageUsageRecordInsertResource.insertRecords(self, data, subject, hostname)

