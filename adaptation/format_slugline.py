#!/home/jeremy/Python3.7Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com>

"""
Pandoc filter using panflute
"""

import panflute as pf
import redis
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from utility.helpers import make_identifier
import attr

@attr.s
class Slugline():
    prefix = attr.ib(default='')
    date =  attr.ib(default='')
    location = attr.ib(default='')

    def __str__(self):
        return f'{self.prefix} {self.date} {self.location}'

rds = redis.Redis(decode_responses=True)

def set_previous_metadata(metadata):
    metadata_index_key = metadate['metadata_index_key']
    metadata_key = make_identifier()
    for k, v in metadata.items():
        rds.hset(metadata_key, k, v)
    rds.rpush(metadata_index_key, metadata_key)
    rds.expire(metadata_index_key, 60)
    rds.expire(metadata_key, 60)

def diff_date(date):
    try:
        prev_date = rds.hget(rds.lindex(metadata_index_key, -1), 'date')
    except:
        return None
    if prev_date:
        return relativedelta(parse(date), parse(prev_date))
    return None


def diff_loc(loc):
    try:
        return loc == rds.hget(rds.lindex(metadata_index_key, -1), 'location')
    except Exception as e:
        print(e)
        return None


def format_slugline(meta):
    date = meta['date']
    loc = meta['location']

    if meta['sequence_start']:
        slugline = Slugline(date=date, location=loc)
    else:

    dd = diff_date(date)
    dl = diff_loc(loc)

    if dd.years > 30:
        slugline = Slugline(prefix ='Returning to modern-day interview')

    elif dd.years < -30:
        slugline = Slugline(prefix='In a flashback to', date=date)

    elif dd.days == 1:
        slugline = Slugline(prefix='The following day')

    elif 1 < dd.days < 5:
        slugline = Slugline(prefix='A few days later')

    else:
        slugline = Slugline()

    if dl:
        slugline.location = loc

    return str(slugline)

def prepare(doc):
    pass

def action(elem, doc):
    pass


def finalize(doc):
    metadata = doc.get_metadata()
    slugline = format_slugline(metadata)
    if slugline:
        doc.metadata["slugline"] = pf.MetaString(str(slugline))
        set_previous_metadata(metadata)
    return doc

def main(doc=None):
    return pf.run_filter(action,
                         prepare=prepare,
                         finalize=finalize,
                         doc=doc)

if __name__ == '__main__':
    main()
