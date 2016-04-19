# -*- coding: utf-8 -*-
"""
Parser to convert cloud usage records in XML format into Python dictionaries,
which are easier to work with.

Author: Magnus Jonsson, HPC2N, Umeå Universitet
Copyright: HPC2N, Umeå Universitet
"""

import time

from twisted.python import log

from sgas.ext import isodate
from sams.nodeavailabilityrecords import arelements as ar

# date constants
ISO_TIME_FORMAT   = "%Y-%m-%dT%H:%M:%SZ" # if we want to convert back some time
JSON_DATETIME_FORMAT = "%Y %m %d %H:%M:%S"


# These should be moved an independant module for reuse


def parseBoolean(value):
    if value == '1' or value.lower() == 'true':
        return True
    elif value == '0' or value.lower() == 'false':
        return False
    else:
        log.msg('Failed to parse value %s into boolean' % value, system='sgas.UsageRecord')
        return None


def parseInt(value):
    try:
        return int(value)
    except ValueError:
        log.msg("Failed to parse float: %s" % value, system='sgas.UsageRecord')
        return None


def parseFloat(value):
    try:
        return float(value)
    except ValueError:
        log.msg("Failed to parse float: %s" % value, system='sgas.UsageRecord')
        return None


def parseISODuration(value):
    try:
        td = isodate.parse_duration(value)
        return (td.days * 3600*24) + td.seconds # screw microseconds
    except ValueError:
        log.msg("Failed to parse duration: %s" % value, system='sgas.UsageRecord')
        return None


def parseISODateTime(value):
    try:
        dt = isodate.parse_datetime(value)
        return time.strftime(JSON_DATETIME_FORMAT, dt.utctimetuple())
    except ValueError, e:
        log.msg("Failed to parse datetime value: %s (%s)" % (value, str(e)), system='sgas.UsageRecord')
        return None
    except isodate.ISO8601Error, e:
        log.msg("Failed to parse ISO datetime value: %s (%s)" % (value, str(e)), system='sgas.UsageRecord')
        return None


# ---

def xmlToDict(ar_doc, insert_identity=None, insert_hostname=None, insert_time=None):
    # Convert a node availability record xml element into a dictionaries
    # only works for one storage record element
    # Use the ursplitter module to split a ar document into seperate elements

    assert ar_doc.tag == ar.NODE_AVAILABILITY_RECORD

    r = {}

    def setIfNotNone(key, value):
        if key is not None:
            r[key] = value

    if insert_identity is not None:
        r['insert_identity'] = insert_identity
    if insert_hostname is not None:
        r['insert_hostname'] = insert_hostname
    if insert_time is not None:
        r['insert_time'] = time.strftime(JSON_DATETIME_FORMAT, insert_time)


    for element in ar_doc:

        if element.tag == ar.RECORD_IDENTITY:
            setIfNotNone('record_id',   element.get(ar.RECORD_ID))
            setIfNotNone('create_time', parseISODateTime(element.get(ar.CREATE_TIME)))

        elif element.tag == ar.SITE:            r['site']           = element.text
        elif element.tag == ar.MACHINE_NAME:    r['machine_name']   = element.text

        elif element.tag == ar.START_TIME:      r['start_time']     = parseISODateTime(element.text)
        elif element.tag == ar.END_TIME:        r['end_time']       = parseISODateTime(element.text)

        elif element.tag == ar.AVAILABLE:       r['available'] = parseInt(element.text)
        elif element.tag == ar.UNAVAILABLE:     r['unavailable'] = parseInt(element.text)
        elif element.tag == ar.RESERVED:        r['reserved'] = parseInt(element.text)
        elif element.tag == ar.UNKNOWN:         r['unknown'] = parseInt(element.text)
        else:
            log.msg("Unhandled node availability record element: %s" % element.tag, system='sgas.NodeAvilability')

    return r

