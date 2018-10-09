from __future__ import absolute_import, unicode_literals

from django.db import models
from datetime import datetime


class ContentsCashe(models.Model):
    hubid = models.CharField(max_length=256)
    itemid = models.CharField(max_length=256)
    parentid = models.CharField(max_length=256)
    text = models.CharField(max_length=64)
    icon = models.CharField(max_length=64)
    lastModifiedTime = models.DateTimeField('date posted', default=datetime.now)

class AutodeskAccounts(models.Model):
    userid = models.CharField(max_length=64)
    username = models.CharField(max_length=64)
    email = models.CharField(max_length=256)
    firstname = models.CharField(max_length=32)
    lastname = models.CharField(max_length=32)
    profileimage_s = models.CharField(max_length=1024)
    profileimage_m = models.CharField(max_length=1024)
