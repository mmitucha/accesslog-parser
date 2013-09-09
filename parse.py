#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import re
import datetime, time

# Inspired by article: http://www.seehuhn.de/blog/52

class Timezone(datetime.tzinfo):
    """Convert timestamp from nginx log"""

    def __init__(self, name="+0000"):
        self.name = name
        seconds = int(name[:-2])*3600+int(name[-2:])*60
        self.offset = datetime.timedelta(seconds=seconds)

    def utcoffset(self, dt):
        return self.offset

    def dst(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return self.name


# Decorator for cleaning dict from parsed line
def clean_parsed_log(fn):
    def wrapped(*args):
        try:
            result_dict = fn(*args)
        except TypeError:
            pass

        # Convert date string to datetime object
        if "datetime" in result_dict:
            tt = time.strptime(result_dict["datetime"][:-6], "%d/%b/%Y:%H:%M:%S")
            tt = list(tt[:6]) + [ 0, Timezone(result_dict["datetime"][-5:]) ]
            result_dict["datetime"] = datetime.datetime(*tt).isoformat()

        if 'status' in result_dict:
            result_dict['status'] = int(result_dict['status'])

        if result_dict["size"] in [0, "0"]:
            result_dict['size'] = None
        else:
            result_dict['size'] = int(result_dict["size"])

        for i in result_dict:
            if result_dict[i] == "-":
                result_dict[i] = None

        return result_dict

    return wrapped


@clean_parsed_log
def parse(line):
    #Parse single line read from 'access.log' file.
    parts = [
        r'(?P<host>\S+)',                   # host %h
        r'\S+',                             # indent %l (unused)
        r'(?P<user>\S+)',                   # user %u
        r'\[(?P<datetime>.+)\]',            # datetime %t
        r'"(?P<request>.+)"',               # request "%r"
        r'(?P<status>[0-9]+)',              # status %>s
        r'(?P<size>\S+)',                   # size %b (careful, can be '-')
        r'"(?P<referer>.*)"',               # referer "%{Referer}i"
        r'"(?P<agent>.*)"',                 # user agent "%{User-agent}i"
    ]
    
    pattern = re.compile(r'\s+'.join(parts)+r'\s*\Z')
    match = pattern.match(line)
    result = match.groupdict()
    return result
