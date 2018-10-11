
# Django Imports
from django.shortcuts import render
from django.shortcuts import redirect

from django.http import HttpResponse
from django.http import HttpRequest
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.http import HttpResponseServerError
from django.http import HttpResponseNotFound
from django.http import HttpResponseForbidden

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template import RequestContext

from django.views.defaults import server_error, bad_request

import json
import urllib
import urlparse
import pprint

from forge_django.settings import base as settings
from home.models import AutodeskAccounts

from lib import log
from lib import httpHelper
from lib import forgeAdopter
from lib import forgeCacheController

# Global Variables
logger = log.Logger()
forgeDM = forgeAdopter.ForgeDataManagementAdopter(settings.ADSK_FORGE['FORGE_CLIENT_ID'], settings.ADSK_FORGE['FORGE_CLIENT_SECRET'])
forgeCC = forgeCacheController.ForgeCacheController(settings.ADSK_FORGE['FORGE_CLIENT_ID'], settings.ADSK_FORGE['FORGE_CLIENT_SECRET'])
forgeOA = forgeAdopter.ForgeOAuthAdopter(settings.ADSK_FORGE['FORGE_CLIENT_ID'], settings.ADSK_FORGE['FORGE_CLIENT_SECRET'])
pp = pprint.PrettyPrinter(indent=4)
http = httpHelper.HttpHelper()
OAUTH_CALLBACK_URL = settings.ADSK_FORGE['FORGE_AUTH_CALLBACK']

'''
======================================================================================================
View Utilities 
======================================================================================================
'''
def get_guestuser():
    account = None

    accounts = AutodeskAccounts.objects.filter(username='guestuser')
    if accounts and len(accounts)>0:
        logger.message('accounts[0].profileimage_m = %s' % accounts[0].profileimage_m)
        account = accounts[0]

    return account


def forge_check_accessToken(request):
    # Check session record of access-token
    IsAutheroized = http.check_if_session_authorized(request)

    # Check expiration of token
    if IsAutheroized:
        # try access token
        try:
            # [MEMO] So far, this api call has most simple variables, it is used for access test.
            response = forgeDM.get_hubs(request.session['token-type'], request.session['access-token'])
        except Exception as e:
            logger.exception(e)

        # refresh token
        if not response:
            logger.message('access token seems to be expired, then try to refresh...')
            response = forgeOA.post_refresh_token(request.session['refresh-token'])
            if not response:
                logger.warning('token refresh is failed !! check Authentication server response messages.')
                IsAutheroized = False
            else:
                logger.message('token refresh is succeeded ...')
                logger.message(json.dumps(response, indent=4))

    return IsAutheroized



'''
======================================================================================================
Request View Handlers
======================================================================================================
'''
def forge_index(request):
    return redirect('forge-home/')

def foge_get_jstree(request):
    # DEBUG
    http.dump_request(request)

    jstree={}
    if (request.method == 'GET'):
        hubid = request.GET.get('hubid')
        if hubid:
            # Get jstree data from DB cache table
            jstree = forgeCC.get_jstree_from_cache(hubid)
            if not jstree:
                # Get BIM360 contents tree
                # jstree = forgeDM.get_jstree_from_hub(hubid, request.session['token-type'], request.session['access-token'])
                forgeCC.update_cache(hubid, request.session['token-type'], request.session['access-token'])
                jstree = forgeCC.get_jstree_from_cache(hubid)

        else:
            bad_request()
    else:
        bad_request()

    return JsonResponse(jstree)



def viewer_ext(request):
    try:
        # DEBUG
        http.dump_request(request)

        # if there is "key" variable, it means session_key has been bridged from redirect source.
        # and, that session has OAuth authorization tokens, that has to be extracted at this step.
        # [MEMO] Because of django session control, usually, the prime session ID of HttpRequest from client and the
        # second session ID of redirect to external OAuth server are different, since it's cross domain communication.
        # Then at this moment, it's necessary to extract the access token across the second session id.
        key = request.GET.get('key')
        if key:
            logger.message("key = %s" % key)
            http.bridge_session_from_key(session_key=key, dest_request=request)

        IsAutheroized = forge_check_accessToken(request)

        guest_account = get_guestuser()
        if guest_account:
            data = {
                'IsAutheroized': IsAutheroized,
                'token': '',
                'expires_in': 0,
                'hublist': None,
                'account': guest_account
            }
        else:
            logger.message('guest accounts is not found. Please check database settings...')
            return server_error(request)

        logger.message('IsAutheroized = %s' % IsAutheroized )
        if IsAutheroized:
                # update autodek account database
                account, created = forgeCC.get_or_create_autodesk_account(request.session['token-type'], request.session['access-token'])

                # get hubs.
                hubs = forgeDM.get_hubs(request.session['token-type'], request.session['access-token'])
                if hubs and 'data' in hubs:
                    hublist = hubs['data']

                    # check if session hubid
                    hubid = http.get_session_hubid(request)
                    if not hubid:
                        hubid = hublist[0]['id']

                    if hubid:
                        data = {
                            'IsAutheroized' : IsAutheroized,
                            'token' : request.session['access-token'],
                            'expires_in': request.session['expires-in'],
                            'hublist' : hublist,
                            'account' : account
                        }
                    else:
                        logger.error('hubid is None.')
                        return server_error(request)
                else:
                    logger.error('get_hubs return None.')
                    logger.error('get_hubs return None.')
                    # Celan up
                    http.clear_session(request)
                    return redirect('api/forge/reset/')
        else:
            # Celan up
            http.clear_session(request)


        #return render_to_response("home/home_page.html", context=data, content_type=RequestContext(request))
        return render(request, 'home/viewer_ext.html', context=data)

    except Exception as e:
        logger.warning(e.message, trace=True)
        return server_error(request)

def forge_home(request):
    try:
        # DEBUG
        http.dump_request(request)

        # if there is "key" variable, it means session_key has been bridged from redirect source.
        # and, that session has OAuth authorization tokens, that has to be extracted at this step.
        # [MEMO] Because of django session control, usually, the prime session ID of HttpRequest from client and the
        # second session ID of redirect to external OAuth server are different, since it's cross domain communication.
        # Then at this moment, it's necessary to extract the access token across the second session id.
        key = request.GET.get('key')
        if key:
            logger.message("key = %s" % key)
            http.bridge_session_from_key(session_key=key, dest_request=request)

        IsAutheroized = forge_check_accessToken(request)

        guest_account = get_guestuser()
        if guest_account:
            data = {
                'IsAutheroized': IsAutheroized,
                'token': '',
                'expires_in': 0,
                'hublist': None,
                'account': guest_account
            }
        else:
            logger.message('guest accounts is not found. Please check database settings...')
            return server_error(request)

        logger.message('IsAutheroized = %s' % IsAutheroized )
        if IsAutheroized:
                # update autodek account database
                account, created = forgeCC.get_or_create_autodesk_account(request.session['token-type'], request.session['access-token'])

                # get hubs.
                hubs = forgeDM.get_hubs(request.session['token-type'], request.session['access-token'])
                if hubs and 'data' in hubs:
                    hublist = hubs['data']

                    # check if session hubid
                    hubid = http.get_session_hubid(request)
                    if not hubid:
                        hubid = hublist[0]['id']

                    if hubid:
                        data = {
                            'IsAutheroized' : IsAutheroized,
                            'token' : request.session['access-token'],
                            'expires_in': request.session['expires-in'],
                            'hublist' : hublist,
                            'account' : account
                        }
                    else:
                        logger.error('hubid is None.')
                        return server_error(request)
                else:
                    # It must be HTTP Error 401: Unauthorized, then clean up session logs.
                    logger.error('get_hubs return None.')
                    # Celan up
                    http.clear_session(request)
                    return redirect('api/forge/reset/')
        else:
            # Celan up
            http.clear_session(request)

        #return render_to_response("home/home_page.html", context=data, content_type=RequestContext(request))
        return render(request, 'home/home_page.html', context=data)

    except Exception as e:
        logger.warning(e.message, trace=True)
        return server_error(request)


def forge_session_reset(request):
    try:
        http.clear_session(request)
        return redirect('/forge-home/')

    except Exception as e:
        logger.warning(e.message)
        return server_error(request)


def forge_get_code_deprecated(request):

    # DEBUG
    http.dump_request(request)

    if 'access-token' in request.session:
        logger.message('session[access-token]=%s' % request.session['access-token'])
        if request.session['access-token']:
            # Turn back to request page
            return redirect(request.META['HTTP_REFERER'])
    else:
        logger.message('session[access-token] is empty')

    try :
        callback = OAUTH_CALLBACK_URL
        requesturl = forgeOA.generate_3l_code_url(callback_url=callback)

        if requesturl:
            logger.message('try redirect!! :: %s' % requesturl)
            response = HttpResponseRedirect(requesturl)
            #response = redirect(requesturl)
            response.__setitem__('Access-Control-Allow-Origin', '*')
            response.__setitem__('Access-Control-Allow-Headers', '*')
            response.__setitem__('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')

            # DEBUG
            #logger.message( response.serialize_headers())

            return response

        else:
            logger.warning('get_3l_code_url faile !!')
            return server_error(request)
    except Exception as e:
        logger.warning(e.message, trace=True)
        return server_error(request)


def forge_3legged_redirect(request):

    # DEBUG
    http.dump_request(request)

    # Check session
    if 'access-token' in request.session:
        logger.message('session[access-token]=%s' % request.session['access-token'])
        if request.session['access-token']:
            # Because it has already access token, turn back to request page
            return redirect(request.META['HTTP_REFERER'])
    else:
        logger.message('session[access-token] is empty')

    try :
        callback = OAUTH_CALLBACK_URL
        #callback = OAUTH_CALLBACK_URL + '/' + request.session['_auth_user_hash']
        requesturl = forgeOA.generate_3l_code_url(callback_url=callback)
        logger.message(requesturl)
        response = HttpResponse(requesturl, content_type='text/plain')
        return response

    except Exception as e:
        logger.warning(e.message, trace=True)
        return server_error(request)


def forge_3legged_callback(request):

    logger.message('forge_callback start !! ----------->>>')

    # DEBUG
    http.dump_request(request)
    #logger.message(pp.pformat(dict(request.user)))

    try :
        result = urlparse.urlparse(request.get_raw_uri())
        logger.message('result.query = %s' % result.query)
        if result is not None:
            query = urlparse.parse_qs(result.query)
            if query:
                logger.message (' parsed query = %s' % query)

                response = forgeOA.post_3l_token(str(query['code'][0]), redirecturl=OAUTH_CALLBACK_URL)
                #response = forgeDM.post_3l_token(str(query['code'][0]), redirecturl=request.path)

                logger.message(json.dumps(response))

                if response:
                    # Save access token and expire sec to current session store dictionary.
                    http.save_session(request, response)

                    # [MEMO] In case of first Autodesk Account login, the request has not yet session_key,
                    # but in case of second or later login, it has already session_key.
                    # To avoid "concatenate error", check whether session_key is exist or not.
                    # [CAUTION] You never select Django session cookie mode,
                    #  since it doesn't work the following session_key inheritation.
                    if request.session.session_key:
                        return HttpResponseRedirect('/forge-home/?key=%s' % request.session.session_key)
                    else:
                        return HttpResponseRedirect('/forge-home/')
                else:
                    return HttpResponse(status=400, content='3 legged access token authentication failed.')

    except Exception as e:
        logger.warning(e.message, trace=True)
        return server_error(request)


def error400(request):
    data = {}
    return render(request, '400.html', data)

def error403(request):
    data = {}
    return render(request, '403.html', data)

def error404(request):
    data = {}
    return render(request, '404.html', data)

def error500(request):
    data = {}
    return render(request, '500.html', data)