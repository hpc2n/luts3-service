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
from sams.cloudrecords import clelements as cl

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

def xmlToDict(cl_doc, insert_identity=None, insert_hostname=None, insert_time=None):
    # Convert a cloud usage record xml element into a dictionaries
    # only works for one storage record element
    # Use the ursplitter module to split a cl document into seperate elements

    assert cl_doc.tag == cl.CLOUD_COMPUTE_RECORD or cl_doc.tag == cl.CLOUD_STORAGE_RECORD

    r = {}

    r['record_type'] = cl_doc.tag

    def setIfNotNone(key, value):
        if key is not None:
            r[key] = value

    if insert_identity is not None:
        r['insert_identity'] = insert_identity
    if insert_hostname is not None:
        r['insert_hostname'] = insert_hostname
    if insert_time is not None:
        r['insert_time'] = time.strftime(JSON_DATETIME_FORMAT, insert_time)


    for element in cl_doc:

        if element.tag == cl.RECORD_IDENTITY:
            setIfNotNone('record_id',   element.get(cl.RECORD_ID))
            setIfNotNone('create_time', parseISODateTime(element.get(cl.CREATE_TIME)))

        elif element.tag == cl.RESOURCE:        r['resource'] = element.text
        elif element.tag == cl.SITE:            r['site'] = element.text
        elif element.tag == cl.PROJECT:         r['project']  = element.text
        elif element.tag == cl.USER:            r['username']  = element.text
        elif element.tag == cl.INSTANCE_ID:     r['instance']  = element.text
        elif element.tag == cl.REGION:          r['region']  = element.text
        elif element.tag == cl.ZONE:            r['zone']  = element.text
        elif element.tag == cl.COST:            r['cost']  = parseFloat(element.text)

        elif element.tag == cl.START_TIME:      r['start_time']     = parseISODateTime(element.text)
        elif element.tag == cl.END_TIME:        r['end_time']       = parseISODateTime(element.text)
        elif element.tag == cl.DURATION:        r['duration']       = parseISODuration(element.text)

        elif cl_doc.tag == cl.CLOUD_STORAGE_RECORD: 
            if element.tag == cl.FILECOUNT:
                r['file_count'] = element.text
            elif element.tag == cl.STORAGETYPE:
                r['storage_type'] = element.text
            elif element.tag == cl.ALLOCATED_DISK:
                r['allocated_disk'] = parseInt(element.text)

        elif cl_doc.tag == cl.CLOUD_COMPUTE_RECORD: 
            if element.tag == cl.FLAVOUR:
                r['flavour'] = element.text
            elif element.tag == cl.ALLOCATED_CPU:
                r['allocated_cpu'] = parseFloat(element.text)
            elif element.tag == cl.ALLOCATED_DISK:
                r['allocated_disk'] = parseInt(element.text)
            elif element.tag == cl.ALLOCATED_MEMORY:
                r['allocated_memory'] = parseInt(element.text)
            elif element.tag == cl.USED_CPU:
                r['used_cpu'] = parseFloat(element.text)
            elif element.tag == cl.USED_DISK:
                r['used_disk'] = parseInt(element.text)
            elif element.tag == cl.USED_MEMORY:
                r['used_memory'] = parseInt(element.text)
            elif element.tag == cl.USED_NETWORK_UP:
                r['used_network_up'] = parseInt(element.text)
            elif element.tag == cl.USED_NETWORK_DOWN:
                r['used_network_down'] = parseInt(element.text)
            elif element.tag == cl.IOPS:
                r['iops'] = parseInt(element.text)

        else:
            log.msg("Unhandled storage record element: %s" % element.tag, system='sgas.CloudRecord')

    return r

