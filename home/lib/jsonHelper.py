import os
import json
import log

class JsonHelper(object):

    def __init__(self, destpath):
        self.dest = destpath
        self.data = {}
        self.logger = log.Logger()

    def ascii_encode_dict(self, data):
        rtn = data
        try:
            ascii_encode = lambda x: x.encode('ascii') if unicode == type(x) else x
            rtn = dict(map(ascii_encode, pair) for pair in data.items())
        except Exception as e:
            self.logger.warning(e.message)
            pass

        return rtn

    def load(self):
        try:
            with open(self.dest, mode='r') as file:
                self.data = json.load(file,  object_hook=self.ascii_encode_dict)
        except Exception as e:
            self.logger.warning(e.message)
        return self.data

    def dump(self, data):
        try:
            with open(self.dest, mode='w') as file:
                json.dump(obj=data, fp=file, encoding='utf-8')
        except Exception as e:
            self.logger.warning(e.message)
