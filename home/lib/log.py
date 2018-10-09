import os
import logging
import pprint
import inspect
import traceback

class Logger(object):

    def __init__(self):
        # create a new logger - django also uses logger and the default
        # output includes all the internal django debug
        self.logger = logging.getLogger('ACCESS')
        self.pp = pprint.PrettyPrinter(indent=4)

    def trace(self):
        f = inspect.currentframe()
        while f :
            msg = str(inspect.getframeinfo(f))
            self.logger.info('     %s' % msg)
            f = f.f_back
    
    def addHeader(self,msg):
        f = inspect.currentframe()
        if f and f.f_back and f.f_back.f_back:
            file = inspect.getframeinfo(f.f_back.f_back)[0]
            if file :
                file = os.path.basename(file)
            line = inspect.getframeinfo(f.f_back.f_back)[1]
            func = inspect.getframeinfo(f.f_back.f_back)[2]
            msg = '[%s(%s)::%s()] %s' % (file, line, func, msg)
        return msg
    
    def debug(self, msg='', trace=False):
        self.logger.debug(self.addHeader(msg))
        if trace:
            self.logger.debug(traceback.format_exc())
    
    def message(self, msg='', trace=False):
        self.logger.info(self.addHeader(msg))
        if trace:
            self.logger.info(traceback.format_exc())

    def error(self, msg ='', trace=False) :
        self.logger.error(self.addHeader(msg))
        if trace:
            self.logger.error(traceback.format_exc())

    def warning(self, msg ='', trace=False) :
        self.logger.warning(self.addHeader(msg))
        if trace:
            self.logger.warning(traceback.format_exc())

    def exception(self, Exception):
        self.error(msg=Exception.message, trace=True)

    def format(self, obj) :
        rtn = None
        if obj is not None:
            if self.pp.isreadable(obj):
                rtn = self.pp.pformat(obj)
            else:
                rtn = '[this object is not readable for pprint]'
        return rtn

#EOF