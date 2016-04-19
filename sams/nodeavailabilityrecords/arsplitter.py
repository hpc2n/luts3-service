# -*- coding: utf-8 -*-
"""
Node Availability Record splitter to split an node availability record XML document (which can
contain one or more records) into a list of node availability records.

Author: Magnus Jonsson, HPC2N, Umeå Universitet
Copyright: HPC2N, Umeå Universitet
"""


from xml.etree import cElementTree as ET

from sams.nodeavailabilityrecords import arelements as ar


class ParseError(Exception):
    """
    Raised when an error occurs during the parsing for splitting up the ur
    elements.
    """


def splitARDocument(ar_data):

    node_availability_records = []

    try:
        tree  = ET.fromstring(ar_data)
    except Exception, e:
        raise ParseError("Error parsing node availability record data (%s)" % str(e))

    if tree.tag == ar.NODE_AVAILABILITY_RECORDS:        
        for ar_element in tree:
            if ar_element.tag == ar.NODE_AVAILABILITY_RECORDS:
                for ar_element2 in ar_element:
                    if not ar_element2.tag == ar.NODE_AVAILABILITY_RECORD:
                        raise ParseError("Subelement in NodeAvailabilityRecords doc not a NodeAvailabilityRecord: " + 
                                    ar_element2.tag)
                    node_availability_records.append(ar_element2)
            else:
                if not ar_element.tag == ar.NODE_AVAILABILITY_RECORD:
                    raise ParseError("Subelement in NodeAvailabilityRecords doc not a NodeAvailabilityRecord: " + ar_element.tag)
                node_availability_records.append(ar_element)

    elif tree.tag == ar.NODE_AVAILABILITY_RECORD:
        node_availability_records.append(tree)

    else:
        raise ParseError("Top element is not NodeAvailabilityRecords or NodeAvailabilityRecord it id: %s" % tree.tag)

    return node_availability_records

