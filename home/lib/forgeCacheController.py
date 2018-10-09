import datetime
import json
import re
import pytz

import forgeAdopter
import log
logger = log.Logger()

from home.models import ContentsCashe
from home.models import AutodeskAccounts

class ForgeCacheController(object):

    def __init__(self, client_id, client_secret):
        self.forgeDM = forgeAdopter.ForgeDataManagementAdopter(client_id, client_secret)
        self.forgeOA = forgeAdopter.ForgeOAuthAdopter(client_id, client_secret)

    def convert_str_to_datetime(self, timestr):
        assert timestr, 'input assertion failed'
        try:
            # strip micro seconds string.
            stripped = re.sub(pattern=r'(^\d+-\d+-\d+T\d+:\d+:\d+)\.(\d+Z)', repl=(r'\1'), string=timestr)
            #logger.message('strapped=%s' % stripped)
            dt = datetime.datetime.strptime(stripped, '%Y-%m-%dT%H:%M:%S')

            # convert naive to aware
            dt = pytz.utc.localize(dt)

        except Exception as e:
            logger.error(e.message, trace=True)

        return dt

    def convert_datetime_to_str(self, timestamp):
        assert timestamp, 'input assertion failed'
        fmt = timestamp.strftime("%Y/%m/%d %H:%M:%S")
        return fmt

    def insert_contents_cache(self, hubid, itemid, parentid, text, icon, lastModifiedTime ):
        '''
        hubid = models.CharField(max_length=256)
        itemid = models.CharField(max_length=256)
        parentid = models.CharField(max_length=256)
        text = models.CharField(max_length=64)
        icon = models.CharField(max_length=64)
        lastModifiedTime = models.DateTimeField('date posted', default=datetime.now)
        '''
        rtn = False
        try:
            # check duplication
            cc = ContentsCashe.objects.get(hubid=hubid, itemid=itemid)
            if cc:
                # check last modified timestamp
                if lastModifiedTime > cc.lastModifiedTime:
                    cc.parentid = parentid
                    cc.text = text
                    cc.icon = icon
                    cc.lastModifiedTime = lastModifiedTime
                    cc.save()
                else:
                    logger.message("no update : %s" % self.convert_datetime_to_str(cc.lastModifiedTime))
            else:
                logger.error('any objects not found.')

        except ContentsCashe.DoesNotExist as e:
            logger.message(e.message, trace=True)
            # add new record
            cc = ContentsCashe(hubid=hubid, itemid=itemid, parentid=parentid, text=text, icon=icon,
                               lastModifiedTime=lastModifiedTime)
            cc.save()

        except ContentsCashe.MultipleObjectsReturned as e:
            logger.error(e.message, trace=True)

        except Exception as e:
            logger.error(e.message, trace=True)

        return rtn


    def update_cache(self, hubid, token_type, token):
        assert  hubid and token_type and token, 'input assertion failed.'
        #self.forgeDM.set_accesstoken(token=token, token_type=token_type)
        data = self.forgeDM.get_jstree_from_hub(hubid, token_type, token)
        for itr in data['core']['data']:
            logger.message("itr = %s" % json.dumps(itr))

            dt = self.convert_str_to_datetime(itr['lastmodtime'])

            self.insert_contents_cache(hubid=hubid,
                                       itemid=itr['id'],
                                       parentid=itr['parent'],
                                       text=itr['text'],
                                       icon=itr['icon'],
                                       lastModifiedTime=dt)

        #self.forgeDM.clear_accesstoken()
        return

    def get_jstree_from_cache(self, hubid):
        assert hubid, 'input assertion failed.'
        jsondata = None
        jstree_array = []

        rows = ContentsCashe.objects.filter(hubid=hubid)
        for itr in rows:
            logger.message('itr.itemid=%s' % itr.itemid)
            row = { 'id':itr.itemid, 'parent':itr.parentid, 'text':itr.text, 'icon':itr.icon }
            jstree_array.append(row)

        if len(jstree_array) > 0 :
            jsondata = {}
            jsondata['core'] = {}
            jsondata['core']['data'] = jstree_array
        
        return jsondata

    def get_or_create_autodesk_account(self, token_type, token):
        '''
        userid = models.CharField(max_length=64)
        username = models.CharField(max_length=64)
        email = models.CharField(max_length=256)
        firstname = models.CharField(max_length=32)
        lastname = models.CharField(max_length=32)
        profileimage_s = models.CharField(max_length=1024)
        profileimage_m = models.CharField(max_length=1024)

        :param token_type:
        :param token:
        :return:
        '''
        account = None
        created = False
        try:
            data = self.forgeOA.get_userprofile_me(token_type=token_type, token=token)
            if data and 'userId' in data:
                account, created = AutodeskAccounts.objects.get_or_create(userid=data['userId'],
                                                       defaults={
                                                           'username' : data['userName'],
                                                           'email' : data['emailId'],
                                                           'firstname' : data['firstName'],
                                                           'lastname': data['lastName'],
                                                           'profileimage_s': data['profileImages']['sizeX20'],
                                                           'profileimage_m': data['profileImages']['sizeX80'],
                                                         })
                logger.message('created = %s' % created)
            else:
                logger.error('get_userprofile_me() failed.')

        except ContentsCashe.MultipleObjectsReturned as e:
            logger.error(e.message, trace=True)

        except Exception as e:
            logger.exception(e)

        return account, created
