"""
Wrapper for saving inserted storage records on file.

Author: Magnus Jonsson
Copyright: HPC2N, Umea Universitet, 2016
"""

from sgas.usagerecord.jobinsertresource import JobUsageRecordInsertResource
from datetime import datetime

class JobUsageRecordInsertResourceSave(JobUsageRecordInsertResource):
    savepath = ""
    savecnt = 0

    def __init__(self, cfg, db, authorizer):
        JobUsageRecordInsertResource.__init__(self,cfg,db,authorizer)
        self.savepath = cfg.get('JobUsageRecordInsertResourceSave','savepath');

    # Save input storage record as file in 'savepath'
    def insertRecords(self, data, subject, hostname):
        try:
            self.savecnt += 1
            outputfile = "%s/ur.%s.%d.xml" % (self.savepath,
                    datetime.now().strftime("%Y%m%d%H%M%S"),self.savecnt)
            f = open(outputfile,"w")
            f.write(data)
            f.close()
        except IOError:
            log.msg('Failed to write file: %s' % outputfile,
                    system='sams.JobUsageRecordInsertResourceSave')
            
        return JobUsageRecordInsertResource.insertRecords(self, data, subject, hostname)

