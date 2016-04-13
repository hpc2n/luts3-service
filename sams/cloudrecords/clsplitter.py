"""
Cloud Record splitter to split an cloud record XML document (which can
contain one or more cloud records) into a list cloud records.

Author: Magnus Jonsson, HPC2N, Umeå Universitet
Copyright: HPC2N, Umeå Universitet
"""


from xml.etree import cElementTree as ET

from sams.cloudrecords import clelements as cl



class ParseError(Exception):
    """
    Raised when an error occurs during the parsing for splitting up the ur
    elements.
    """


def splitCLDocument(cl_data):

    cloud_records = []

    try:
        tree  = ET.fromstring(cl_data)
    except Exception, e:
        raise ParseError("Error parsing cloud record data (%s)" % str(e))

    if tree.tag == cl.CLOUD_RECORDS:        
        for cl_element in tree:
            if cl_element.tag == cl.CLOUD_RECORDS:
                for cl_element2 in cl_element:
                    if not cl_element2.tag == cl.CLOUD_COMPUTE_RECORD and not cl_element2.tag == cl.CLOUD_STORAGE_RECORD:
                        raise ParseError("Subelement in CloudRecords doc not a Cloud{Compute,Storage}Record: " + 
                                    cl_element2.tag)
                    cloud_records.append(cl_element2)
            else:
                if not cl_element.tag == cl.STORAGE_USAGE_RECORD:
                    raise ParseError("Subelement in CloudRecords doc not a Cloud{Compute,Storage}Record: " + 
                                cl_element.tag)
                cloud_records.append(cl_element)

    elif tree.tag == cl.CLOUD_COMPUTE_RECORD or tree.tag == cl.CLOUD_STORAGE_RECORD:
        cloud_records.append(tree)

    else:
        raise ParseError("Top element is not CloudRecords or Cloud{Compute,Storage}Record:: %s != %s" % (tree.tag, cl.CLOUD_RECORDS))

    return cloud_records

