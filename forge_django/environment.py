import os
import json
import sys
import socket

# global variable
ENV_CONFIG = {}
ENVIRONMENT_TYPE = ''
FORGE_CLIENT_ID =  ''
FORGE_CLIENT_SECRET = ''
FORGE_AUTH_CALLBACK = ''

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
    rtn = "Development"
    try:
        hostname = socket.gethostname()
        if hostname :
            if ENV_CONFIG.has_key('host_map') and ENV_CONFIG['host_map'].has_key(hostname):
                rtn = ENV_CONFIG['host_map'][hostname]
            else:
                raise SystemError('"HOSTNAME"=[%s] is invalid for env_config.json' % hostname)
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