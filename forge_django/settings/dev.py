#=======================================================================================================================
#   Copyright (c) Autodesk, Inc. All rights reserved
#   Written by Yusuke Mori, Autodesk Consulting 2018
#
#   This software is provided as is, without any warranty that it will work. You choose to use this tool at your own risk.
#   Neither Autodesk nor the authors can be taken as responsible for any damage this tool can cause to
#   your data. Please always make a back up of your data prior to use this tool.
#
#=======================================================================================================================

from __future__ import absolute_import, unicode_literals

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'f(21tx$)q+m*xlrl4x9x#(l($90e3ki4t3bih8q*kxw=zazba9'


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


try:
    from .local import *
except ImportError:
    pass
