#=======================================================================================================================
#   Copyright (c) Autodesk, Inc. All rights reserved
#   Written by Yusuke Mori, Autodesk Consulting 2018
#
#   This software is provided as is, without any warranty that it will work. You choose to use this tool at your own risk.
#   Neither Autodesk nor the authors can be taken as responsible for any damage this tool can cause to
#   your data. Please always make a back up of your data prior to use this tool.
#
#=======================================================================================================================

import os
import json
import sys
import socket

# global variable
ENV_CONFIG = {}
ENV_HOSTNAME = ''
ENVIRONMENT_TYPE = ''
FORGE_CLIENT_ID =  ''
FORGE_CLIENT_SECRET = ''
FORGE_AUTH_CALLBACK = ''
ALLOWED_HOSTS = ''

def ascii_encode_dict(data):
    rtn = data
    try:
        ascii_encode = lambda x: x.encode('ascii') if unicode == type(x) else x
        rtn = dict(map(ascii_encode, pair) for pair in data.items())
    except Exception as e:
        print e.message
        pass

    return rtn

def loadEnvJson():
    global ENV_CONFIG
    try:
        path = os.path.join(os.path.dirname(__file__), 'environment.json')
        with open(path, mode='r') as file :
            # [MEMO] Specifically, 'file_server_host' key needs to be ascii code strictly.
            # Then this json encoding needs hook conversion from json default utf-8 to ascii.
            ENV_CONFIG = json.load(file, object_hook=ascii_encode_dict)
    except Exception as e:
        raise Exception


def getEnvironmentType():
    global ENV_HOSTNAME
    rtn = "Development"
    try:
        ENV_HOSTNAME = socket.gethostname()
        if ENV_HOSTNAME :
            if ENV_CONFIG.has_key('host_map') and ENV_CONFIG['host_map'].has_key(ENV_HOSTNAME):
                rtn = ENV_CONFIG['host_map'][ENV_HOSTNAME]
            else:
                raise SystemError('"HOSTNAME"=[%s] is invalid for env_config.json' % ENV_HOSTNAME)
        else:
            raise SystemError('Environemnt variable "HOSTNAME" not found !!')
    except Exception as e:
        raise Exception
    return rtn


try:
    loadEnvJson()
    ENVIRONMENT_TYPE = getEnvironmentType()
    if ENVIRONMENT_TYPE:
        FORGE_CLIENT_ID = ENV_CONFIG['type_definition'][ENVIRONMENT_TYPE]['FORGE_CLIENT_ID']
        FORGE_CLIENT_SECRET = ENV_CONFIG['type_definition'][ENVIRONMENT_TYPE]['FORGE_CLIENT_SECRET']
        FORGE_AUTH_CALLBACK = ENV_CONFIG['type_definition'][ENVIRONMENT_TYPE]['FORGE_AUTH_CALLBACK']
        ALLOWED_HOSTS = ENV_CONFIG['type_definition'][ENVIRONMENT_TYPE]['ALLOWED_HOSTS']
    else:
        raise SystemError('getEnvironmentType() failed. Please check if current hostname and environment.json is matched.')


except EnvironmentError as e:
    print e.message
    raise EnvironmentError

except ImportError as e:
    print e.message
    raise ImportError

except Exception as e:
    print e.message
    raise Exception