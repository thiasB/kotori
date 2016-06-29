# -*- coding: utf-8 -*-
# (c) 2014-2016 Andreas Motl <andreas.motl@elmyra.de>
import re
import os
import sys
import shelve
import socket
import logging
import json_store
from uuid import uuid4
from appdirs import user_data_dir
from datetime import timedelta

logger = logging.getLogger()

def slm(message):
    """sanitize log message"""
    return unicode(message).replace('{', '{{').replace('}', '}}')

class Singleton(object):
    """
    Singleton class by Duncan Booth.
    Multiple object variables refers to the same object.
    http://www.suttoncourtenay.org.uk/duncan/accu/pythonpatterns.html
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance


class ConfigStoreShelve(dict):

    store = None

    def __init__(self):
        if not ConfigStore.store:
            print "ConfigStoreShelve.__init__"
            self.app_data_dir = user_data_dir('kotori', 'elmyra')
            if not os.path.exists(self.app_data_dir):
                os.makedirs(self.app_data_dir)
            self.config_file = os.path.join(self.app_data_dir, 'config')
            ConfigStore.store = shelve.open(self.config_file, writeback=True)

    def has_key(self, key):
        return ConfigStore.store.has_key(key)

    def __getitem__(self, key):
        print 'ConfigStoreShelve.__getitem__'
        return ConfigStore.store[key]

    def __setitem__(self, key, value):
        print 'ConfigStoreShelve.__setitem__', key, value
        ConfigStore.store[key] = value
        ConfigStore.store.sync()


class ConfigStoreJson(dict):

    store = None

    def __init__(self):
        if not ConfigStoreJson.store:
            #print "ConfigStoreJson.__init__"
            self.app_data_dir = user_data_dir('kotori-daq', 'Elmyra')
            logger.debug("ConfigStoreJson app_data_dir: {}".format(self.app_data_dir))
            if not os.path.exists(self.app_data_dir):
                os.makedirs(self.app_data_dir)
            self.config_file = os.path.join(self.app_data_dir, 'config.json')
            ConfigStoreJson.store = json_store.open(self.config_file)

    def has_key(self, key):
        return ConfigStoreJson.store.has_key(key)

    def __getitem__(self, key):
        #print 'ConfigStoreJson.__getitem__'
        return ConfigStoreJson.store[key]

    def __setitem__(self, key, value):
        #print 'ConfigStoreJson.__setitem__', key, value
        ConfigStoreJson.store[key] = value
        ConfigStoreJson.store.sync()


class NodeId(Singleton):

    config = None
    NODE_ID = 'NODE_UNKNOWN'

    def __init__(self):
        if not self.config:
            self.config = ConfigStoreJson()
        if not self.config.has_key('uuid'):
            self.config['uuid'] = str(uuid4())
        self.NODE_ID = self.config['uuid']
        logger.debug("NODE ID: {}".format(self.NODE_ID))

    def __str__(self):
        return str(self.NODE_ID)


def get_hostname():
    return socket.gethostname()

def setup_logging(level=logging.INFO):
    log_format = '%(asctime)-15s [%(name)-25s] %(levelname)-7s: %(message)s'
    logging.basicConfig(
        format=log_format,
        stream=sys.stderr,
        level=level)

    # TODO: Control debug logging of HTTP requests through yet another commandline option "--debug-http" or "--debug-requests"
    requests_logger = logging.getLogger('requests')
    requests_logger.setLevel(logging.WARN)


def tdelta(input):
    # https://blog.posativ.org/2011/parsing-human-readable-timedeltas-in-python/
    keys = ["weeks", "days", "hours", "minutes", "seconds"]
    regex = "".join(["((?P<%s>\d+)%s ?)?" % (k, k[0]) for k in keys])
    kwargs = {}
    for k,v in re.match(regex, input).groupdict(default="0").items():
        kwargs[k] = int(v)
    return timedelta(**kwargs)

