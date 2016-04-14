"""
Wrapper for saving inserted cloud records on file.

Author: Magnus Jonsson
Copyright: HPC2N, Umea Universitet, 2016
"""

from sams.cloudrecords.cloudinsertresource import CloudUsageRecordInsertResource
from datetime import datetime

class CloudUsageRecordInsertResourceSave(CloudUsageRecordInsertResource):
    savepath = ""
    savecnt = 0

    def __init__(self, cfg, db, authorizer):
        CloudUsageRecordInsertResource.__init__(self,cfg,db,authorizer)
        self.savepath = cfg.get('CloudUsageRecordInsertResourceSave','savepath');

    # Save input storage record as file in 'savepath'
    def insertRecords(self, data, subject, hostname):
        try:
            self.savecnt += 1
            outputfile = "%s/cr.%s.%d.xml" % (self.savepath,
                    datetime.now().strftime("%Y%m%d%H%M%S"),self.savecnt)
            f = open(outputfile,"w")
            f.write(data)
            f.close()
        except IOError:
            log.msg('Failed to write file: %s' % outputfile,
                    system='sams.CloudUsageRecordInsertResourceSave')
            
        return CloudUsageRecordInsertResource.insertRecords(self, data, subject, hostname)

