# -*- coding: utf-8 -*-
"""
XML elements for SAMS cloud record specification.

Author: Magnus Jonsson, HPC2N
Copyright: HPC2N, Umeå Universitet
"""


from xml.etree.cElementTree import QName


# namespace
AR_NAMESPACE = "http://sams.snic.se/namespaces/2016/04/nodeavailabilityrecords"

# record identity and metadata
NODE_AVAILABILITY_RECORDS = QName("{%s}NodeAvailabilityRecords" % AR_NAMESPACE)
NODE_AVAILABILITY_RECORD  = QName("{%s}NodeAvailabilityRecord"  % AR_NAMESPACE)
RECORD_IDENTITY           = QName("{%s}RecordIdentity"          % AR_NAMESPACE)
RECORD_ID                 = QName("{%s}recordId"                % AR_NAMESPACE)
CREATE_TIME               = QName("{%s}createTime"              % AR_NAMESPACE)

# system
SITE                      = QName("{%s}Site"                    % AR_NAMESPACE)
MACHINE_NAME              = QName("{%s}MachineName"             % AR_NAMESPACE)

# Time & Dates
START_TIME                = QName("{%s}StartTime"               % AR_NAMESPACE)
END_TIME                  = QName("{%s}EndTime"                 % AR_NAMESPACE)

# Available
AVAILABLE                  = QName("{%s}Available"              % AR_NAMESPACE)
UNAVAILABLE                = QName("{%s}Unavailable"            % AR_NAMESPACE)
RESERVED                   = QName("{%s}Reserved"               % AR_NAMESPACE)
UNKNOWN                    = QName("{%s}Unknown"                % AR_NAMESPACE)
