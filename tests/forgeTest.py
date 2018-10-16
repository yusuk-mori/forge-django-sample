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
import sys
import unittest
import json
import datetime
import re
import shutil

sys.path.append('%s/../' % os.path.dirname(__file__) )
sys.path.append('%s/../../' % os.path.dirname(__file__) )
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forge_django.settings.dev")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import RequestFactory

from forge_django.settings import dev as settings
from home.lib import log
from home.lib import httpHelper
from home.lib import jsonHelper
from home import views as homeViews
logger = log.Logger()
http = httpHelper.HttpHelper()
jsonhlp = jsonHelper.JsonHelper(destpath=r"C:\log\sessionlog.json")
TEST_HUB_ID = 'b.236fcd1d-6e21-442f-b514-d5abd1a9eaa3'

class ForgeTestSuite(unittest.TestCase):
    def test_01_forgeRequest(self):
        from home.lib import forgeAdopter

        forge = forgeAdopter.ForgeDataManagementAdopter(settings.ADSK_FORGE['FORGE_CLIENT_ID'], settings.ADSK_FORGE['FORGE_CLIENT_SECRET'])
        session = jsonhlp.load()

        #token = 'eyJhbGciOiJIUzI1NiIsImtpZCI6Imp3dF9zeW1tZXRyaWNfa2V5In0.eyJ1c2VyaWQiOiJROVYyTVVNN0xUN1MiLCJleHAiOjE1Mzc1MjUxNDYsInNjb3BlIjpbImRhdGE6cmVhZCJdLCJjbGllbnRfaWQiOiJaUnFMR09CZWFmeWdIeERXMWhkUXc1TVNxVkE2SVdXSSIsImdyYW50X2lkIjoicmJOeXNzRXlKdXNRSkRNQjJWZTMyNXJ4S2llWW5na3ciLCJhdWQiOiJodHRwczovL2F1dG9kZXNrLmNvbS9hdWQvand0ZXhwNjAiLCJqdGkiOiJ6MEhqNldaR1NCUEg3ZUFXNlBDSWRMNW90eThTeW0wMmZLOG1jRzJKOHpsTExNWm51UDExVFpHZTFEV0tOeDVqIn0.pD9ElqmpLsDdDFLPW56e7jNbHUIlZVo-xuPTgcRBCKs'
        token = session['access-token']

        hubid = TEST_HUB_ID
        hubid2 = ''
        #urn = 'adsk.wipprod:dm.lineage:4Tx3Myl_TYaiJy44vyUXPw'
        urn = 'adsk.wipprod:dm.lineage:qF3iLEvvSbK3hNGt7v-bvw'

        try:
            hubs = forge.get_hubs('Bearer', token, hubid)
            logger.message('hubs = %s' % hubs )

            projs = forge.get_projects(hubid, 'Bearer', token)
            logger.message('projs = %s' % projs )

            #thumbnail = forge.get_thumbnail(token, urn)
            #logger.message('thumbnail =' + str(thumbnail))

        except Exception as e:
            logger.message(e.message, trace=True)
            return False

        return True

    def test_02_refreshtoken(self):
        from home.lib import forgeAdopter
        try:
            forge = forgeAdopter.ForgeOAuthAdopter(settings.ADSK_FORGE['FORGE_CLIENT_ID'], settings.ADSK_FORGE['FORGE_CLIENT_SECRET'])
            session = jsonhlp.load()

            #token = 'EDHChaiUI5XfrD+rmrLznExcltz5NCqv8wL8Dn6ujnRjjvPnlVL3paK7UvlZh/gTXduelwRNA2PrhMQPLQZY/g=='
            token = session['refresh-token']

            res = forge.post_refresh_token(token)


        except Exception as e:
            logger.message(e.message, trace=True)
            return False

        return True

    def test_03_getItems(self):
        from home.lib import forgeAdopter
        try:
            forge = forgeAdopter.ForgeDataManagementAdopter(settings.ADSK_FORGE['FORGE_CLIENT_ID'], settings.ADSK_FORGE['FORGE_CLIENT_SECRET'])

            hubid = TEST_HUB_ID

            session = jsonhlp.load()
            token = session['access-token']

            projs = forge.get_projects(hubid, 'Bearer', token)
            if projs and len(projs['data']) > 0:
                #logger.message('projs = %s' % json.dumps(projs['data'][0], indent=4))
                projid = projs['data'][0]['id']
                topdata = forge.get_project_topfolder(hubid=hubid, projectid=projid, token_type=session['token-type'], token=session['access-token'])

                if topdata and len(topdata['data']) > 0:
                    for index in range(0, len(topdata['data'])):
                        iditr = topdata['data'][index]['id']
                        logger.message('id = %s' % iditr)

                        #items = forge.post_command_listitems(projectid=projid, resourceid=iditr, token_type=session['token-type'], token=session['access-token'])

                        items = forge.get_folder_contents(projectid=projid, folderid=iditr, token_type=session['token-type'], token=session['access-token'])

                        logger.message(json.dumps(items, indent=4))

                else:
                    logger.message('forge.get_project_topfolder does not return any data')
                    return False
            else:
                logger.message('forge.get_projects does not return any project')
                return False

        except Exception as e:
            logger.message(e.message, trace=True)
            return False

        return True

    def test_04_getTree(self):
        from home.lib import forgeAdopter
        try:
            forge = forgeAdopter.ForgeDataManagementAdopter(settings.ADSK_FORGE['FORGE_CLIENT_ID'], settings.ADSK_FORGE['FORGE_CLIENT_SECRET'])

            hubid = TEST_HUB_ID

            session = jsonhlp.load()
            token = session['access-token']

            projs = forge.get_projects(hubid, 'Bearer', token)
            if projs and len(projs['data']) > 0:
                #logger.message('projs = %s' % json.dumps(projs['data'][0], indent=4))
                projid = projs['data'][0]['id']
                topdata = forge.get_project_topfolder(hubid=hubid, projectid=projid, token_type=session['token-type'], token=session['access-token'])

                if topdata and len(topdata['data']) > 0:
                    for index in range(0, len(topdata['data'])):
                        iditr = topdata['data'][index]['id']
                        logger.message('id = %s' % iditr)

                        #items = forge.get_contents_tree_recurce(projectid=projid, target_resid=iditr, token_type=session['token-type'], token=session['access-token'], recurce=0)
                        items = forge.get_contents_jstree_list(projectid=projid, target_resid=iditr, token_type=session['token-type'], token=session['access-token'])
                        logger.message(json.dumps(items, indent=4))

                else:
                    logger.message('forge.get_project_topfolder does not return any data')
                    return False
            else:
                logger.message('forge.get_projects does not return any project')
                return False

        except Exception as e:
            logger.message(e.message, trace=True)
            return False

        return True

    def test_05_postJob(self):
        from home.lib import forgeAdopter
        rtn = True
        try:
            forge = forgeAdopter.ForgeDataManagementAdopter(settings.ADSK_FORGE['FORGE_CLIENT_ID'], settings.ADSK_FORGE['FORGE_CLIENT_SECRET'])
            forgeMDR = forgeAdopter.ForgeModelDerivativeAdopter(settings.ADSK_FORGE['FORGE_CLIENT_ID'], settings.ADSK_FORGE['FORGE_CLIENT_SECRET'])

            hubid = TEST_HUB_ID

            session = jsonhlp.load()
            token = session['access-token']
            forge.set_accesstoken(token_type=session['token-type'], token=session['access-token'])
            forgeMDR.set_accesstoken(token_type=session['token-type'], token=session['access-token'])

            projs = forge.get_projects(hubid, 'Bearer', token)
            if projs and len(projs['data']) > 0:
                #logger.message('projs = %s' % json.dumps(projs['data'][0], indent=4))
                projid = projs['data'][0]['id']
                topdata = forge.get_project_topfolder(hubid=hubid, projectid=projid, token_type=session['token-type'], token=session['access-token'])

                if topdata and len(topdata['data']) > 0:
                    for index in range(0, len(topdata['data'])):
                        iditr = topdata['data'][index]['id']
                        logger.message('id = %s' % iditr)

                        logger.message('try get_contents_first_item !!!!!!!!!!!')
                        first = forge.get_contents_first_item(projectid=projid, target_resid=iditr, search='')

                        logger.message('pass get_contents_first_item !!!!!!!!!!!')
                        logger.message(json.dumps(first, indent=4))

                        if first:
                            logger.message('try post_derivative_job !!!!!!!!!!!')
                            #res = forgeMDR.post_derivative_job(urn=first['id'], root_file=first['attributes']['extension']['data']['sourceFileName'])
                            # res = forgeMDR.post_derivative_job(urn=first['id'],root_file='compress_name.rvt')
                            res = forgeMDR.get_manifest(urn=first['id'])

                            logger.message(json.dumps(res, indent=4))

                else:
                    logger.message('forge.get_project_topfolder does not return any data')
                    rtn = False
            else:
                logger.message('forge.get_projects does not return any project')
                rtn = False

        except Exception as e:
            logger.message(e.message, trace=True)
            rtn = False
        finally:
            if forge:
                forge.clear_accesstoken()
                forgeMDR.clear_accesstoken()

        return rtn

    def test_06_updateCache(self):
        from home.lib import forgeAdopter
        from home.lib import forgeCacheController
        rtn = True
        try:
            forgeDM = forgeAdopter.ForgeDataManagementAdopter(settings.ADSK_FORGE['FORGE_CLIENT_ID'], settings.ADSK_FORGE['FORGE_CLIENT_SECRET'])
            cacheCtl = forgeCacheController.ForgeCacheController(settings.ADSK_FORGE['FORGE_CLIENT_ID'], settings.ADSK_FORGE['FORGE_CLIENT_SECRET'])

            session = jsonhlp.load()
            token = session['access-token']
            #forge.set_accesstoken(token_type=session['token-type'], token=session['access-token'])

            hubid = TEST_HUB_ID

            cacheCtl.update_cache(hubid, token_type=session['token-type'], token=session['access-token'])

        except Exception as e:
            logger.message(e.message, trace=True)
            rtn = False
        finally:
            if forgeDM:
                forgeDM.clear_accesstoken()

        return rtn

    def test_07_getHubs(self):
        from home.lib import forgeAdopter
        rtn = True
        try:
            session = jsonhlp.load()
            token = session['access-token']
            # forge.set_accesstoken(token_type=session['token-type'], token=session['access-token'])

            forgeDM = forgeAdopter.ForgeDataManagementAdopter()
            data = forgeDM.get_hubs(token_type=session['token-type'], token=session['access-token'])

            if data:
                logger.message(json.dumps(data, indent=4))

        except Exception as e:
            logger.message(e.message, trace=True)
            rtn = False
        return rtn

    def test_08_getJstreeCache(self):
        from home.lib import forgeCacheController
        rtn = True
        try:
            cacheCtl = forgeCacheController.ForgeCacheController(settings.ADSK_FORGE['FORGE_CLIENT_ID'], settings.ADSK_FORGE['FORGE_CLIENT_SECRET'])

            session = jsonhlp.load()
            token = session['access-token']
            #forge.set_accesstoken(token_type=session['token-type'], token=session['access-token'])

            hubid = TEST_HUB_ID
            data = cacheCtl.get_jstree_from_cache(hubid)

            logger.message(json.dumps(data, indent=4))

        except Exception as e:
            logger.message(e.message, trace=True)
            rtn = False

        return rtn

    def test_09_getProfileMe(self):
        from home.lib import forgeAdopter
        rtn = True
        try:
            forgeOA = forgeAdopter.ForgeOAuthAdopter(settings.ADSK_FORGE['FORGE_CLIENT_ID'], settings.ADSK_FORGE['FORGE_CLIENT_SECRET'])
            session = jsonhlp.load()
            token = session['access-token']

            hubid = 'b.236fcd1d-6e21-442f-b514-d5abd1a9eaa3'
            data = forgeOA.get_userprofile_me(token_type=session['token-type'], token=session['access-token'])
            logger.message(json.dumps(data, indent=4))

        except Exception as e:
            logger.message(e.message, trace=True)
            rtn = False

        return rtn

    def test_10_checkPermissions(self):
        from home.lib import forgeAdopter
        rtn = True
        try:
            forgeDM = forgeAdopter.ForgeDataManagementAdopter(settings.ADSK_FORGE['FORGE_CLIENT_ID'], settings.ADSK_FORGE['FORGE_CLIENT_SECRET'])
            session = jsonhlp.load()
            token = session['access-token']

            hubid = TEST_HUB_ID
            forgeDM.set_accesstoken(token_type=session['token-type'], token=session['access-token'])
            projs = forgeDM.get_projects(hubid=hubid)
            top = forgeDM.get_project_topfolder(hubid=hubid, projectid=projs['data'][0]['id'])
            logger.message(json.dumps(top, indent=4))
            data = forgeDM.post_command_checkpermission(project_id=projs['data'][0]['id'], target_urn=top['data'][0]['id'])
            logger.message(json.dumps(data, indent=4))

        except Exception as e:
            logger.message(e.message, trace=True)
            rtn = False

        return rtn



    def test_99_dummyRequest(self):

        userlist = User.objects.filter(username='moriy')
        if len(userlist) > 0:
            user = userlist[0]
            factory = RequestFactory()

            req = factory.get('forge-home/')
            req.user = user

            res = homeViews.forge_home(req)

            logger.message(res)
            #http.dump_request(req)

        else:
            logger.message('test user not found')


class Help(unittest.TestCase ):
    def test_dumpattributes(self):

        import inspect
        thismodule = inspect.getmodule(self)
        classes = map(lambda x: x[0], inspect.getmembers( thismodule , inspect.isclass))
        #classes = [DBTestSuite, DBPreparationTestSuite, DBCleanUpTestSuite]

        for classname in classes:
            suite = getattr(thismodule, classname)
            print '%s ------------>>[Test Cases]' % '{:<48}'.format(suite)
            for attr in dir(suite):
                if attr.startswith('test_'):
                    print '    %s' % attr


if __name__ == "__main__":
    unittest.main()
