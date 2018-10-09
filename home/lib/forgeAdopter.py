import requests
import urllib
import urllib2
import urllib3
import json
import pprint
import base64
import re

import log
logger = log.Logger()

class ForgeBaseAdopter(object):
    def __init__(self, client_id, client_secret):
        self.base_url = 'https://developer.api.autodesk.com'
        self.pp = pprint.PrettyPrinter(indent=4)
        self.client_id = client_id
        self.client_secret = client_secret
        self.current_token = None
        self.current_token_type = None
        self.__debug = True

    def get_credentials (self) :
        """
        get clienet id and secret dictionary
        :return: dictionary type
        {
            'id': self.client_id,
            'secret': self.client_secret
        }
        """
        return {
            'id': self.client_id,
            'secret': self.client_secret
        }

    def get_by_urllib2(self, url, headers=None, data=None, isjson=True):
        """
        urllib2 wrapper
        Some of Forge GET type API needs to be set params in its Header,
        but Python requests.get() method has no interface to set sutome headers,
        Because of it, in python implementation, urllib2 wrapper is needed.
        :param url:
        :param headers:
        :param data:
        :return: json format response
        """
        response = None
        assert url, "url is invalid"
        try :
            if data:
                encoded = urllib.urlencode(data)
            else:
                encoded = None

            req = urllib2.Request(url, data=encoded, headers=headers)

            opener = urllib2.urlopen(req)
            stream = opener.read()

            if stream:
                if isjson:
                    response = json.loads(stream)
                else:
                    response = stream
            else:
                logger.message('response.read() return Noen !!')

        except urllib2.URLError as e:
            logger.error(e.message, trace=True)
        except Exception as e:
            logger.error(e.message, trace=True)

        return response

    def set_accesstoken(self, token, token_type):
        """
        set access token. After you finished all api requests, you should call clear_accesstoken()
        [CAUTION!!] Be careful not to confuse across multi sessions.
        this is just short cut for composed task consists of multi api requests.
        :param token:
        :param token_type:
        :return: None
        """
        assert token and token_type, 'access token assertion failed.'
        self.current_token = token
        self.current_token_type = token_type

    def clear_accesstoken(self):
        """
        clear current access token.
        :return:
        """
        self.current_token = None
        self.current_token_type = None

    def get_auth_header(self, in_token_type=None, in_token=None, data=None):

        if in_token_type:
            token_type = in_token_type
        else:
            token_type = self.current_token_type

        if in_token:
            token = in_token
        else:
            token = self.current_token

        headers = {
            'Authorization': token_type + ' ' + token
        }

        if data:
            for key in data.keys():
                headers[key]=data[key]

        return headers

    def get_urlencode_quote(self, data):
        """
        Because python2 urllib.urlencode can only 'urllib.quote_plus' encoding.
        But OAuth needs not + but %20 encode.
        Python3 resolve it by urllib.parse.quote(), but Python2 can't.
        https://docs.python.jp/2/library/urllib.html
        :param data:
        :return:
        """
        query = urllib.urlencode(data)
        query = re.sub(pattern='\+', repl='%20', string=query)

        return query

    def get(self, add_url, headers=None, data=None):
        """
        GET method on Python 2.X
        :param add_url:
        :param headers:
        :param data:
        :return: json response
        """
        assert add_url and add_url.startswith('/') , 'add_url assertion failed.'
        rtn = None
        url_api = self.base_url + add_url

        if self.__debug:
            logger.message('---------------------------------------------------------')
            logger.message('----------------------- HTTP GET ------------------------')
            logger.message('---------------------------------------------------------')
            logger.message('[ url ] : %s' % url_api)
            if headers:
                logger.message(r'[ header ] :')
                logger.message(json.dumps(headers, indent=4))
            if data:
                logger.message(r'[ data ] :')
                logger.message(json.dumps(data, indent=4))
            logger.message('---------------------------------------------------------')
            logger.message('---------------------------------------------------------')
            logger.message('---------------------------------------------------------')

        try :
            rtn = self.get_by_urllib2(url_api, headers, data)

        except Exception as e:
            logger.error(e.message, trace=True)

        return rtn

    def post(self, add_url, headers=None, data=None):
        """
        POST method on Python 2.X
        :param add_url:
        :param headers:
        :param data:
        :return: json response
        """
        url_api = self.base_url + add_url

        if self.__debug:
            logger.message('---------------------------------------------------------')
            logger.message('----------------------- HTTP POST -----------------------')
            logger.message('---------------------------------------------------------')
            logger.message('[ url ] : %s' % url_api)
            if headers:
                logger.message(r'[ header ] :')
                logger.message(json.dumps(headers, indent=4))
            if data:
                logger.message(r'[ data ] :')
                logger.message(json.dumps(data, indent=4))
            logger.message('---------------------------------------------------------')
            logger.message('---------------------------------------------------------')
            logger.message('---------------------------------------------------------')

        try:
            encoded = data
            if 'Content-Type' in headers:
                if 'json' in headers['Content-Type']:
                    encoded = json.dumps(data)
                elif 'x-www-form-urlencoded' in headers['Content-Type']:
                    encoded=urllib.urlencode(data)

            response = requests.post(url_api, data=encoded, headers=headers)
            if 200 == response.status_code:
                return response.json()
            else:
                logger.warning('status_code : %s' % response.status_code)
                logger.warning('reason      : %s' % response.reason)
                logger.warning('message     : %s' % self.pp.pformat(response.content))

        except Exception as e:
            logger.error(e.message, trace=True)

        return None

    def delete(self, add_url, headers=None, data=None):
        """
        DELETE method on Python 2.X
        :param add_url:
        :param headers:
        :param data:
        :return:
        """
        url_api = self.base_url + add_url

        response = requests.delete(url_api, data=json.dumps(data), headers=headers)

        if 200 == response.status_code:
            return response.json()

        return None

    def redirect(self, add_url, headers=None, data=None):
        url = self.base_url + add_url
        response = None

        assert url, "url is invalid"
        try :
            if data:
                encoded = urllib.urlencode(data)
            else:
                encoded = None

            req = urllib2.Request(url, data=encoded, headers=headers)

            opener = urllib2.build_opener(urllib2.HTTPRedirectHandler)
            response = opener.open(req)

            if response:
                logger.message('response=[%s]' % (response))
            else:
                logger.message('response.read() return Noen !!')

        except urllib2.URLError as e:
            logger.error(e.message, trace=True)
        except Exception as e:
            logger.error(e.message, trace=True)

        return response


class ForgeDataManagementAdopter(ForgeBaseAdopter):

    def __init__(self, client_id, client_secret):
        super(ForgeDataManagementAdopter, self).__init__(client_id, client_secret)

    def get_hubs(self, token_type=None, token=None, hubid=None):
        """
        Get Forge Hubs
        GET: "Authorization: Bearer nFRJxzCD8OOUr7hzBwbr06D76zAT" "https://developer.api.autodesk.com/project/v1/hubs"
        :param token_type:
        :param token:
        :param hubid:
        :return:
        """
        assert token_type and token, 'input assertion failed.'
        add_url = '/project/v1/hubs'
        if hubid:
            add_url += '/%s' % hubid

        headers = self.get_auth_header(in_token=token, in_token_type=token_type)
        return self.get(add_url=add_url, headers=headers)


    def get_projects(self, hubid, token_type=None, token=None, projectid=None):
        """
        Get Forge Hubs projects
        GET: https://developer.api.autodesk.com/project/v1/hubs/:hub_id/projects
        GET: https://developer.api.autodesk.com/project/v1/hubs/:hub_id/projects/:project_id
        :param hubid:
        :param token_type:
        :param token:
        :param projectid:
        :return:
        """
        assert hubid, 'input assertion failed.'
        add_url = '/project/v1/hubs/%s/projects' % hubid

        if projectid:
            add_url += '/%s' % projectid

        headers = self.get_auth_header(in_token_type=token_type, in_token=token)
        return self.get(add_url=add_url, headers=headers)


    def get_project_topfolder(self, hubid, projectid, token_type=None, token=None):
        """
        Get Project Top Folder
        GET: https://developer.api.autodesk.com/project/v1/hubs/:hub_id/projects/:project_id/topFolders
        :param hubid:
        :param projectid:
        :param token_type:
        :param token:
        :return:
        """
        assert  hubid and projectid, 'input assertion failed.'
        add_url = '/project/v1/hubs/%s/projects/%s/topFolders' % (hubid, projectid)
        headers = self.get_auth_header(in_token_type=token_type, in_token=token)
        return self.get(add_url=add_url, headers=headers)


    def get_folder_contents(self, projectid, folderid, token_type=None, token=None):
        """
        Get Project Contents
        GET: https://developer.api.autodesk.com/data/v1/projects/:project_id/folders/:folder_id/contents
        :param projectid:
        :param folderid:
        :param token_type:
        :param token:
        :return:
        """
        assert projectid and folderid, 'input assertion failed.'
        add_url = '/data/v1/projects/%s/folders/%s/contents' % (projectid, folderid)
        headers = self.get_auth_header(in_token_type=token_type, in_token=token)
        return self.get(add_url=add_url, headers=headers)


    def post_command_listitems(self, projectid, resourceid, token_type=None, token=None):
        """
        Post command ListItems
        POST : https://developer.api.autodesk.com/data/v1/projects/:project_id/commands
        :param projectid:
        :param resourceid:
        :param token_type:
        :param token:
        :return:
        """
        assert projectid and resourceid, 'input assertion failed.'

        add_url = '/data/v1/projects/%s/commands' % (projectid)
        headers = self.get_auth_header(in_token_type=token_type, in_token=token, data={ 'Content-Type' : 'application/vnd.api+json'} )
        body = {
            "jsonapi": {
                "version": "1.0"
            },
            "data": {
                "type": "commands",
                "attributes": {
                    "extension": {
                        "type": "commands:autodesk.core:ListItems",
                        "version": "1.0.0"
                    }
                },
                "relationships": {
                    "resources": {
                        "data": [
                            {
                                "type": "items",
                                "id": "%s" % resourceid
                            }
                        ]
                    }
                }
            }
        }

        logger.message(json.dumps(body, indent=4))
        return self.post(add_url=add_url, headers=headers, data=body)


    def post_command_checkpermission(self, project_id, target_urn, token_type=None, token=None):
        """
        https://developer.api.autodesk.com/data/v1/projects/:project_id/commands
        :param project_id:
        :param token_type: target folder urn
        :param token:
        :return:
        """
        assert project_id and target_urn, "input assertion failed"
        add_url = '/data/v1/projects/:project_id/commands'
        headers = self.get_auth_header(in_token_type=token_type, in_token=token, data={ 'Content-Type' : 'application/vnd.api+json'} )

        data= {
            "type": "commands",
            "attributes": {
              "extension": {
                "type": "commands:autodesk.core:CheckPermission",
                "version": "1.0.0",
                "data": {
                  "requiredActions": [
                    "read",
                    "view"
                  ]
                }
              }
            },
            "relationships": {
              "resources": {
                "data": [
                  {
                    "type": "folders",
                    "id": target_urn,
                  }
                ]
              }
            }
        }

        hasPermission = False

        response = self.post(add_url, headers=headers, data=data)
        if response:
            hasPermission = response['data']['attributes']['extension']['data']['permissions'][0]['permission']

        return hasPermission

    def get_contents_tree_recurce(self, projectid, target_resid, token_type, token, recurse=0):
        """
        Get folder tree
        :param projectid:
        :param target_resid:
        :param token_type:
        :param token:
        :param recurse:
        :return:
        """

        logger.message('get_contents_tree_recurce : recurce=%d' % recurse)
        treedata = {}

        items = self.get_folder_contents(projectid=projectid, folderid=target_resid, token_type=token_type, token=token)
        if items and len(items['data']) > 0:
            for index in range(0, len(items['data'])):
                # DEBUG
                logger.message(json.dumps(items['data'][index], indent=4))

                type = items['data'][index]['type']
                id = items['data'][index]['id']
                name = items['data'][index]['attributes']['displayName']
                treedata[id] = {'type' : type , 'name' : name }

                if 'folders' == type and recurse < 10:
                    recurse += 1
                    child_tree = self.get_contents_tree_recurce(projectid, id, token_type, token, recurse)
                    if child_tree :
                        treedata[id]['child'] = child_tree
                    recurse -= 1
        # DEBUG
        # logger.message(json.dumps(treedata, indent=4))

        return treedata

    def get_contents_first_item(self, projectid, target_resid, search, token_type=None, token=None, recurse=0):
        logger.message('get_contents_first_item : recurce=%d' % recurse)
        firstitem = None

        items = self.get_folder_contents(projectid=projectid, folderid=target_resid, token_type=token_type, token=token)
        if items and len(items['data']) > 0:
            for index in range(0, len(items['data'])):
                # logger.message(json.dumps(items['data'][index], indent=4))
                type = items['data'][index]['type']
                id = items['data'][index]['id']

                if 'items' == type:
                    firstitem = items['data'][index]
                    logger.message(json.dumps(firstitem, indent=4))
                    break

                elif 'folders' == type and recurse < 10:
                    recurse += 1
                    firstitem = self.get_contents_first_item(projectid, id, search, token_type, token, recurse)
                    recurse -= 1
                    if firstitem:
                        logger.message(json.dumps(firstitem, indent=4))
                        break

        return firstitem


    def get_contents_jstree_list_recurse(self, projectid, target_resid, token_type, token, recurse=0):
        """
        Get folder tree
        [MEMO] jstree json data format is something like below :
         $('#jstree').jstree({'core': {
             'data': [
                 {"id": "ajson1", "parent": "#", "text": "Simple root node"},
                 {"id": "ajson2", "parent": "#", "text": "Root node 2"},
                 {"id": "ajson3", "parent": "ajson2", "text": "Child 1", "icon": "jstree-file",},
                 {"id": "ajson4", "parent": "ajson2", "text": "Child 2", "icon": "jstree-file",},
             ]
         }});
        :param projectid:
        :param target_resid:
        :param token_type:
        :param token:
        :param recurse:
        :return:
        """


        logger.message('get_contents_jstree_list_recurse : recurce=%s' % recurse)
        items_array = []

        items = self.get_folder_contents(projectid=projectid, folderid=target_resid, token_type=token_type, token=token)
        if items and len(items['data']) > 0:
            for index in range(0, len(items['data'])):
                # DEBUG
                logger.message(json.dumps(items['data'][index], indent=4))
                type = items['data'][index]['type']
                text = items['data'][index]['attributes']['displayName']
                lastmod = items['data'][index]['attributes']['lastModifiedTime']

                if 0 == recurse :
                    parent = '#'
                else:
                    parent = target_resid

                if 'folders' == type :
                    icon = "jstree-folder"
                    id = items['data'][index]['id']
                else:
                    icon = "jstree-file"
                    id = items['data'][index]['relationships']['tip']['data']['id']

                itr = { 'id':id, 'parent':parent, 'text':text, 'icon':icon, 'lastmodtime':lastmod }
                items_array.append(itr)

                if 'folders' == type and recurse < 10:
                    recurse += 1
                    new_list = self.get_contents_jstree_list_recurse(projectid, id, token_type, token, recurse)
                    items_array.extend(new_list)
                    recurse -= 1
        # DEBUG
        # logger.message(json.dumps(treedata, indent=4))

        return items_array


    def get_contents_jstree_list(self, projectid, target_resid, token_type, token):
        """
        Get folder tree
        :param projectid:
        :param target_resid:
        :param token_type:
        :param token:
        :return:
        """
        logger.message('get_contents_jstree_list : start!')

        try :
            jsondata = {}

            items_array = self.get_contents_jstree_list_recurse(projectid, target_resid, token_type, token, recurse=0)

            jsondata['core'] = {}
            jsondata['core']['data'] = items_array
        except Exception as e:
            logger.warning(e.message, trace=True)

        return jsondata


    def get_jstree_from_hub(self, hubid, token_type, token):
        """
        Get folder tree
        :param token_type:
        :param token:
        :return:
        """
        assert hubid and token_type and token, "input assertion failed"
        items = {}
        try:
            projs = self.get_projects(hubid, 'Bearer', token)
            if projs and len(projs['data']) > 0:
                #logger.message('projs = %s' % json.dumps(projs['data'][0], indent=4))
                projid = projs['data'][0]['id']
                topdata = self.get_project_topfolder(hubid=hubid, projectid=projid, token_type=token_type, token=token)

                if topdata and len(topdata['data']) > 0:
                    for index in range(0, len(topdata['data'])):
                        iditr = topdata['data'][index]['id']
                        logger.message('id = %s' % iditr)

                        items = self.get_contents_jstree_list(projectid=projid, target_resid=iditr, token_type=token_type, token=token)
                        logger.message(json.dumps(items, indent=4))
                else:
                    logger.message('forge.get_project_topfolder does not return any data')
                    return None
            else:
                logger.message('forge.get_projects does not return any project')
                return None

        except Exception as e:
            logger.message(e.message, trace=True)
            return None

        return items


    #////////////////////////////////////////////////////////////////////
    # Get Forge thumbnail
    #
    #////////////////////////////////////////////////////////////////////
    def get_thumbnail(slef, token, urn):

        base_url = 'https://developer.api.autodesk.com'
        url = base_url + '/modelderivative/v2/designdata/{}/thumbnail?{}'

        query = 'width=400&height=400'

        headers = {
            'Authorization': 'Bearer ' + token['access_token']
        }

        r = requests.get(url.format(urn, query), headers=headers)

        if 200 == r.status_code:
            return r.content

        return None


class ForgeModelDerivativeAdopter(ForgeBaseAdopter):
    def __init__(self, client_id, client_secret):
        super(ForgeModelDerivativeAdopter, self).__init__(client_id, client_secret)

    def get_derivative_formats(self, token_type=None, token=None):
        #  https://developer.api.autodesk.com/modelderivative/v2/designdata/formats
        add_url = '/modelderivative/v2/designdata/formats'
        headers = self.get_auth_header(in_token_type=token_type, in_token=token)
        return self.get(add_url, headers)

    def get_thumbnail(self, urn, token_type=None, token=None ):
        #  https://developer.api.autodesk.com/modelderivative/v2/designdata/:urn/thumbnail
        add_url = '/modelderivative/v2/designdata/%s/thumbnail' % urn
        headers = self.get_auth_header(in_token_type=token_type, in_token=token)
        return self.get(add_url, headers)

    def get_manifest(self, urn, token_type=None, token=None ):
        assert  urn , 'urn assertion faild'
        #  https://developer.api.autodesk.com/modelderivative/v2/designdata/:urn/manifest
        add_url = '/modelderivative/v2/designdata/%s/manifest' % base64.urlsafe_b64encode(urn)
        headers = self.get_auth_header(in_token_type=token_type, in_token=token)
        return self.get(add_url, headers)

    def delete_manifest(self, urn, token_type=None, token=None ):
        assert  urn , 'urn assertion faild'
        #  https://developer.api.autodesk.com/modelderivative/v2/designdata/:urn/manifest
        add_url = '/modelderivative/v2/designdata/%s/manifest' % base64.urlsafe_b64encode(urn)
        headers = self.get_auth_header(in_token_type=token_type, in_token=token)
        return self.delete(add_url, headers)

    def get_metadata(self, urn, guid=None, token_type=None, token=None ):
        assert  urn , 'urn assertion faild'
        # https://developer.api.autodesk.com/modelderivative/v2/designdata/:urn/metadata
        # https://developer.api.autodesk.com/modelderivative/v2/designdata/:urn/metadata/:guid
        add_url = '/modelderivative/v2/designdata/%s/metadata' % base64.urlsafe_b64encode(urn)

        if guid:
            add_url += '/%s' % guid

        headers = self.get_auth_header(in_token_type=token_type, in_token=token)
        return self.get(add_url, headers)

    def get_metadata_properties(self, urn, guid, token_type=None, token=None ):
        assert  urn and guid, 'urn or guid assertion faild'
        #  https://developer.api.autodesk.com/modelderivative/v2/designdata/:urn/metadata/:guid/properties
        add_url = '/modelderivative/v2/designdata/%s/metadata/%s/properties' % (urn, guid)
        headers = self.get_auth_header(in_token_type=token_type, in_token=token)
        return self.get(add_url, headers)

    def post_derivative_job(self, urn, root_file, format='svf', token_type=None, token=None):
        #  https://developer.api.autodesk.com/modelderivative/v2/designdata/job
        add_url = '/modelderivative/v2/designdata/job'
        headers = self.get_auth_header(in_token_type=token_type, in_token=token, data={ 'Content-Type' : 'application/json;  charset=utf-8'} )

        base64urn = base64.urlsafe_b64encode(urn)

        logger.message('base64urn : %s' % base64urn)

        data = {
         "input": {
           "urn": base64urn,
           "compressedUrn": True,
           "rootFilename": root_file
         },
         "output": {
           "destination": {
             "region": "us"
           },
           "formats": [
             {
               "type": format,
               "views": [
                 "2d",
                 "3d"
               ]
             }
           ]
         }
       }

        return self.post(add_url, headers=headers, data=data)

class ForgeOAuthAdopter(ForgeBaseAdopter):
    def __init__(self, client_id, client_secret):
        super(ForgeOAuthAdopter, self).__init__(client_id, client_secret)

    def post_2l_token(self):
        '''
        Get Forge 2-Legged token
        https://developer.api.autodesk.com/authentication/v1/authenticate
        :return:
        '''
        #
        add_url = '/authentication/v1/authenticate'
        headers = {'Content-Type' : 'application/x-www-form-urlencoded'}
        data = {
            'grant_type': 'client_credentials',
            'client_secret': self.client_secret,
            'client_id': self.client_id,
            'scope': 'data:read'
        }
        return self.post(add_url=add_url,headers=headers,data=data)

    def generate_3l_code_url(self, callback_url):
        '''
        Get url+query for Forge 3-Legged code

        ex.
        <a href="https://developer.api.autodesk.com/authentication/v1/authorize?response_type=code& \
         client_id=obQDn8P0GanGFQha4ngKKVWcxwyvFAGE&redirect_uri=http%3A%2F%2Fsampleapp.com%2Foauth%2Fcallback%3Ffoo%3Dbar& \
         scope=data:read">Click here to grant access to your data!</a>

        :return:
        '''
        url_api = self.base_url + '/authentication/v1/authorize'
        data = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': callback_url,
            'scope': 'viewables:read data:read data:write'
        }

        #query = urllib.urlencode(data)
        query = self.get_urlencode_quote(data)

        url = url_api + '?' + query

        logger.message('url=%s' % url)
        return url

    def post_3l_token(self, code, redirecturl):
        '''
        Get Forge 3-Legged token by code
        https://developer.api.autodesk.com/authentication/v1/gettoken
        :param code: temporary code from /authentication/v1/authorize API.
        :return: HttpResponse
        '''
        url_api = self.base_url + '/authentication/v1/gettoken'

        header = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Access-Control-Request-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods':'GET, POST, OPTIONS'
        }

        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'redirect_uri' : redirecturl,
            'code': code
        }

        r = requests.post(url_api, data=data, headers=header)
        logger.message(r.url)

        if 200 == r.status_code:
            return r.json()
        else:
            logger.warning(r.reason)

        return None

    def post_refresh_token(self, token):
        '''
        Post request Forge token refresh
        https://developer.api.autodesk.com/authentication/v1/refreshtoken

        :param token: refresh token
        :return: HttpResponse
        '''
        add_url = '/authentication/v1/refreshtoken'
        header = {'Content-Type': 'application/x-www-form-urlencoded'}

        data = {
            'client_secret': self.client_secret,
            'client_id': self.client_id,
            'grant_type': 'refresh_token',
            'refresh_token' : token
        }

        # return self.post(add_url, data=urllib.urlencode(data), headers=header)
        return self.post(add_url, data=data, headers=header)

    def get_userprofile_me(self, token_type=None, token=None ):
        '''
        https://developer.api.autodesk.com/userprofile/v1/users/@me
        :param token_type:
        :param token:
        :return:
        '''
        add_url = '/userprofile/v1/users/@me'
        headers = self.get_auth_header(in_token_type=token_type, in_token=token)
        return self.get(add_url=add_url, headers=headers)




class ForgeBIM360Adopter(ForgeBaseAdopter):
    def __init__(self, client_id, client_secret):
        super(ForgeBIM360Adopter, self).__init__(client_id, client_secret)

    def get_user_permission(self, container_id, token_type=None, token=None ):
        '''
        https://developer.api.autodesk.com/issues/v1/containers/:container_id/users/me
        '''
        add_url = '/issues/v1/containers/%s/users/me' % container_id
        headers = self.get_auth_header(in_token_type=token_type, in_token=token)
        return self.get(add_url, headers)

