# -*- coding: utf-8 -*-
"""
Software Accounting Record splitter to split an software accounting record XML document (which can
contain one or more records) into a list of software accounting records.

Author: Magnus Jonsson, HPC2N, Umeå Universitet
Copyright: HPC2N, Umeå Universitet
"""


from xml.etree import cElementTree as ET

from sams.softwareaccountingrecords import elements as sa


class ParseError(Exception):
    """
    Raised when an error occurs during the parsing for splitting up the ur
    elements.
    """


def splitDocument(data):

    records = []

    try:
        tree  = ET.fromstring(data)
    except Exception, e:
        raise ParseError("Error parsing software accounting record data (%s)" % str(e))

    if tree.tag == sa.SOFTWARE_ACCOUNTING_RECORDS:
        for element in tree:
            if element.tag == sa.SOFTWARE_ACCOUNTING_RECORDS:
                for element2 in element:
                    if not element2.tag == sa.SOFTWARE_ACCOUNTING_RECORD:
                        raise ParseError("Subelement in SoftwareAccoutingRecords doc not a SoftwareAccountingRecord: " + element2.tag)
                    records.append(element2)
            else:
                if not element.tag == sa.SOFTWARE_ACCOUNTING_RECORD:
                    raise ParseError("Subelement in SoftwareAccoutingRecords doc not a SoftwareAccountingRecord: " + element.tag)
                records.append(element)

    elif tree.tag == sa.NODE_AVAILABILITY_RECORD:
        records.append(tree)

    else:
        raise ParseError("Top element is not SoftwareAccoutingRecords or SoftwareAccountingRecord it id: %s" % tree.tag)

    return records

