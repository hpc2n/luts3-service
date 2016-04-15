"""
Wrapper for saving inserted node availability records on file.

Author: Magnus Jonsson
Copyright: HPC2N, Umea Universitet, 2016
"""

from sams.nodeavailabilityrecords.nodeavailabilityinsertresource import NodeAvailabilityRecordInsertResource
from datetime import datetime

class NodeAvailabilityRecordInsertResourceSave(NodeAvailabilityRecordInsertResource):
    savepath = ""
    savecnt = 0

    def __init__(self, cfg, db, authorizer):
        NodeAvailabilityRecordInsertResource.__init__(self,cfg,db,authorizer)
        self.savepath = cfg.get('NodeAvailabilityRecordInsertResourceSave','savepath');

    # Save input storage record as file in 'savepath'
    def insertRecords(self, data, subject, hostname):
        try:
            self.savecnt += 1
            outputfile = "%s/ar.%s.%d.xml" % (self.savepath,
                    datetime.now().strftime("%Y%m%d%H%M%S"),self.savecnt)
            f = open(outputfile,"w")
            f.write(data)
            f.close()
        except IOError:
            log.msg('Failed to write file: %s' % outputfile,
                    system='sams.NodeAvailabilityRecordInsertResourceSave')
            
        return NodeAvailabilityRecordInsertResource.insertRecords(self, data, subject, hostname)

