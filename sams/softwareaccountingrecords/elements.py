# -*- coding: utf-8 -*-
"""
XML elements for SAMS software accounting record specification.

Author: Magnus Jonsson, HPC2N
Copyright: HPC2N, Umeå Universitet
"""


from xml.etree.cElementTree import QName

# namespace
SA_NAMESPACE = "http://sams.snic.se/namespaces/2019/01/softwareaccountingrecords"

# record identity and metadata
SOFTWARE_ACCOUNTING_RECORDS = QName("{%s}SoftwareAccountingRecords" % SA_NAMESPACE)
SOFTWARE_ACCOUNTING_RECORD  = QName("{%s}SoftwareAccountingRecord"  % SA_NAMESPACE)
RECORD_IDENTITY           = QName("{%s}RecordIdentity"          % SA_NAMESPACE)
RECORD_ID                 = QName("{%s}recordId"                % SA_NAMESPACE)
CREATE_TIME               = QName("{%s}createTime"              % SA_NAMESPACE)

# Job Record information
JOB_RECORD_ID             = QName("{%s}JobRecordID"             % SA_NAMESPACE)

# Software Information
SOFTWARE                   = QName("{%s}Software"              % SA_NAMESPACE)
NAME                       = QName("{%s}Name"                  % SA_NAMESPACE)
VERSION                    = QName("{%s}Version"                % SA_NAMESPACE)
LOCAL_VERSION              = QName("{%s}LocalVersion"                % SA_NAMESPACE)
USER_PROVIDED              = QName("{%s}UserProvided"                % SA_NAMESPACE)
USAGE                      = QName("{%s}Usage"                % SA_NAMESPACE)
