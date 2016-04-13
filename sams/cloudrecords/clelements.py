"""
XML elements for SAMS cloud record specification.

Author: Magnus Jonsson, HPC2N
Copyright: HPC2N, Umeå Universitet
"""


from xml.etree.cElementTree import QName


# namespace
CL_NAMESPACE = "http://sams.snic.se/namespaces/2016/04/cloudrecords"

# record identity and metadata
CLOUD_RECORDS           = QName("{%s}CloudRecords"          % CL_NAMESPACE)
CLOUD_COMPUTE_RECORD    = QName("{%s}CloudComputeRecord"    % CL_NAMESPACE)
CLOUD_STORAGE_RECORD    = QName("{%s}CloudStorageRecord"    % CL_NAMESPACE)
RECORD_IDENTITY         = QName("{%s}RecordIdentity"        % CL_NAMESPACE)
RECORD_ID               = QName("{%s}recordId"              % CL_NAMESPACE)
CREATE_TIME             = QName("{%s}createTime"            % CL_NAMESPACE)

# storage system
SITE                    = QName("{%s}Site"                  % CL_NAMESPACE)
PROJECT                 = QName("{%s}Project"               % CL_NAMESPACE)
USER                    = QName("{%s}User"                  % CL_NAMESPACE)
INSTANCE_ID             = QName("{%s}InstanceId"            % CL_NAMESPACE)

# Time & Dates
START_TIME              = QName("{%s}StartTime"             % CL_NAMESPACE)
END_TIME                = QName("{%s}EndTime"               % CL_NAMESPACE)
DURATION                = QName("{%s}Duration"              % CL_NAMESPACE)

# Type of Resource
REGION                  = QName("{%s}Region"                % CL_NAMESPACE)
ZONE                    = QName("{%s}Zone"                  % CL_NAMESPACE)
FLAVOUR                 = QName("{%s}Flavour"               % CL_NAMESPACE)
COST                    = QName("{%s}Cost"                  % CL_NAMESPACE)
STORAGETYPE             = QName("{%s}StorageType"           % CL_NAMESPACE)

# Allocated
ALLOCATED_CPU           = QName("{%s}AllocatedCPU"          % CL_NAMESPACE)
ALLOCATED_DISK          = QName("{%s}AllocatedDisk"         % CL_NAMESPACE)
ALLOCATED_MEMORY        = QName("{%s}AllocatedMemory"       % CL_NAMESPACE)

# Used
USED_CPU                = QName("{%s}UsedCPU"               % CL_NAMESPACE)
USED_DISK               = QName("{%s}UsedDisk"              % CL_NAMESPACE)
USED_MEMORY             = QName("{%s}UsedMemory"            % CL_NAMESPACE)
USED_NETWORK_UP         = QName("{%s}UsedNetworkUp"         % CL_NAMESPACE)
USED_NETWORK_DOWN       = QName("{%s}UsedNetworkDown"       % CL_NAMESPACE)
IOPS                    = QName("{%s}IOPS"                  % CL_NAMESPACE)
FILECOUNT               = QName("{%s}FileCount"             % CL_NAMESPACE)
