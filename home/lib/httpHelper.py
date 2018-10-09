import pprint
import os
import log

import json
import jsonHelper
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session

# DEBUG/DEV
jsonhlp = jsonHelper.JsonHelper(destpath=r'C:\log\sessionlog.json')

class HttpHelper(object):
    def __init__(self):
        self.pp = pprint.PrettyPrinter(indent=8)
        self.logger = log.Logger()
        pass

    def get_session_hubid(self, request):
        hubid = None
        if 'hubid' in request.session :
            hubid = request.session['hubid']
        return hubid

    def check_if_session_authorized(self, request):
        # Check session access-token
        IsAutheroized = False
        if 'access-token' in request.session and 'expires-in' in request.session and 'token-type' in request.session and 'refresh-token' in request.session :
            self.logger.message('session[access-token]=%s' % request.session['access-token'])
            IsAutheroized = True

        return IsAutheroized

    def save_session_hubid(self, request, hubid):
        assert request and hubid, 'assertion failed.'
        request.session['hubid'] = hubid
        return

    def save_session(self, request, response):
        assert request and response, 'assertion failed.'
        try:

            if 'access-token' in request.session:
                self.logger.debug('session[access-token]=%s' % request.session['access-token'])
            else:
                self.logger.debug('session[access-token] is empty')

            request.session['access-token'] = response['access_token']
            request.session['expires-in'] = response['expires_in']
            request.session['token-type'] = response['token_type']
            request.session['refresh-token'] = response['refresh_token']

            # ONLY DEVELOPMENT MODE
            # os.environ['FORGE_SESSION_TOKEN'] = response['access_token']
            jsonhlp.dump(dict(request.session))

        except Exception as e:
            self.logger.warning(e.message, tarce=True)
        return

    def clear_session(self, request):
        if 'access-token' in request.session:
            del request.session['access-token']
        if 'expires-in' in request.session:
            del request.session['expires-in']
        if 'token-type' in request.session:
            del request.session['token-type']
        if 'refresh-token' in request.session:
            del request.session['refresh-token']
        return

    def bridge_session_from_key(self, session_key, dest_request):
        assert session_key and dest_request, 'input assertion failed.'
        try:
            #ss = SessionStore(session_key=session_key)
            ssitr = Session.objects.get(pk=session_key)
            if ssitr:
                ss = ssitr.get_decoded()

                if ss :
                    self.logger.message(json.dumps(dict(ss), indent=4))

                    assert 'access-token' in ss and 'expires-in' in ss and 'token-type' in ss and 'refresh-token' in ss, \
                        "specified session[ %s ] key assertion failed." % session_key

                    dest_request.session['access-token'] = ss['access-token']
                    dest_request.session['expires-in'] = ss['expires-in']
                    dest_request.session['token-type'] = ss['token-type']
                    dest_request.session['refresh-token'] = ss['refresh-token']


                    self.logger.message(json.dumps(dict(dest_request.session), indent=4))

                else:
                    self.logger.warning('Session.get_decoded() failed. please check if session_key is valid.')
            else:
                self.logger.warning('Session.objects.get() failed. please check if session_key is valid.')

        except Exception as e:
            self.logger.exception(e)

        return

    def dump_request(self, request, meta=False, verbose=False):

        assert request, 'assertion failed'
        self.logger.message('---------------------------------------------------------')
        self.logger.message('---------------------------------------------------------')
        self.logger.message('-----------------------HTTP REQUEST----------------------')
        self.logger.message('---------------------------------------------------------')
        self.logger.message('---------------------------------------------------------')
        self.logger.message('[ General Info ]-----------------------------------------')
        self.logger.message('    method         : %s' % self.pp.pformat(request.method))
        self.logger.message('    path           : %s' % self.pp.pformat(request.path))
        self.logger.message('    path_info      : %s' % self.pp.pformat(request.path_info))
        self.logger.message('    content_type   : %s' % self.pp.pformat(request.content_type))
        self.logger.message('    content_params : %s' % self.pp.pformat(request.content_params))
        self.logger.message('[ request.COOKIES ]--------------------------------------')
        self.logger.message('\n%s' % json.dumps(dict(request.COOKIES), indent=8))
        self.logger.message('[ request.session ]--------------------------------------')
        self.logger.message('    session_key : %s' % request.session.session_key)
        self.logger.message('\n%s' % json.dumps(dict(request.session), indent=8))

        if request.user:
            self.logger.message('[ request.user ]-----------------------------------------')
            self.logger.message('    user.username : %s' % self.pp.pformat(request.user.username))
        if meta:
            self.logger.message('[ request.META ]-----------------------------------------')
            self.logger.message('\n    %s' % self.pp.pformat(dict(request.META)))
        if verbose:
            self.logger.message('[ Verbose Info ]-----------------------------------------')
            self.logger.message('    %s' % self.pp.pformat(request.__dict__))

        self.logger.message('---------------------------------------------------------')
        self.logger.message('---------------------------------------------------------')
        self.logger.message('---------------------------------------------------------')
        self.logger.message('---------------------------------------------------------')
        self.logger.message('---------------------------------------------------------')
        return