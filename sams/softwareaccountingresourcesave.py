"""
Wrapper for saving inserted software accounting records on file.

Author: Magnus Jonsson
Copyright: HPC2N, Umea Universitet, 2016
"""

from sams.softwareaccountingrecords.softwareaccountinginsertresource import SoftwareAccountingRecordInsertResource
from datetime import datetime

class SoftwareAccountingRecordInsertResourceSave(SoftwareAccountingRecordInsertResource):
    savepath = ""
    savecnt = 0

    def __init__(self, cfg, db, authorizer):
        SoftwareAccountingRecordInsertResource.__init__(self,cfg,db,authorizer)
        self.savepath = cfg.get('SoftwareAccountingRecordInsertResourceSave','savepath');

    # Save input storage record as file in 'savepath'
    def insertRecords(self, data, subject, hostname):
        try:
            self.savecnt += 1
            outputfile = "%s/sa.%s.%d.xml" % (self.savepath,
                    datetime.now().strftime("%Y%m%d%H%M%S"),self.savecnt)
            f = open(outputfile,"w")
            f.write(data)
            f.close()
        except IOError:
            log.msg('Failed to write file: %s' % outputfile,
                    system='sams.SoftwareAccountingRecordInsertResourceSave')
            
        return SoftwareAccountingRecordInsertResource.insertRecords(self, data, subject, hostname)

