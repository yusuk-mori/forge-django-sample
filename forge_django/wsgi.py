#=======================================================================================================================
#   Copyright (c) Autodesk, Inc. All rights reserved
#   Written by Yusuke Mori, Autodesk Consulting 2018
#
#   This software is provided as is, without any warranty that it will work. You choose to use this tool at your own risk.
#   Neither Autodesk nor the authors can be taken as responsible for any damage this tool can cause to
#   your data. Please always make a back up of your data prior to use this tool.
#
#=======================================================================================================================

"""
WSGI config for forge_django project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

from __future__ import absolute_import, unicode_literals

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forge_django.settings.dev")

application = get_wsgi_application()
