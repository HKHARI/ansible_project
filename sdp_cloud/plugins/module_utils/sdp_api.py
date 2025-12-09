# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
from ansible.module_utils.urls import fetch_url
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.oauth import get_access_token

try:
    import urllib.parse as urllib_parse
except ImportError:
    import urllib
    urllib_parse = urllib


class SDPClient:
    def __init__(self, module):
        self.module = module
        self.params = module.params
        self.domain = self.params.get('domain')
        self.portal = self.params.get('portal_name')
        self.auth_token = self.params.get('auth_token')
        
        # OAuth params
        self.client_id = self.params.get('client_id')
        self.client_secret = self.params.get('client_secret')
        self.refresh_token = self.params.get('refresh_token')
        self.dc = self.params.get('dc')

        self.base_url = "https://{0}/app/{1}/api/v3".format(self.domain, self.portal)

    def request(self, endpoint, method='GET', data=None):
        """Make API Request"""
        if not self.auth_token:
            # If auth_token not provided, generate it
            if self.client_id and self.client_secret and self.refresh_token:
                token_data = get_access_token(self.module, self.client_id, self.client_secret, self.refresh_token, self.dc)
                self.auth_token = token_data['access_token']
            else:
                self.module.fail_json(msg="Missing authentication credentials. Provide either 'auth_token' or ('client_id', 'client_secret', 'refresh_token', 'dc').")

        url = "{0}/{1}".format(self.base_url, endpoint)
        
        headers = {
            'Authorization': 'Zoho-oauthtoken {0}'.format(self.auth_token),
            'Accept': 'application/v3+json'
        }
        
        payload = None
        if data:
            payload = urllib_parse.urlencode({'input_data': json.dumps(data)})
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

        response, info = fetch_url(
            self.module,
            url,
            data=payload,
            method=method,
            headers=headers
        )

        if not response:
            _handle_error(self.module, info, "API Request Failed")

        body = response.read()
        if not body:
            return {"status": info.get('status'), "msg": "Empty response body", "headers": info.get('headers')}

        try:
            return json.loads(body)
        except ValueError:
            self.module.fail_json(msg="Invalid JSON response from SDP API", raw_response=body)


def _handle_error(module, info, default_msg):
    error_msg = info.get('msg', default_msg)
    response_body = info.get('body')
    
    if response_body:
        try:
            err_body = json.loads(response_body)
            # SDP Cloud V3 API Error Structure
            if 'response_status' in err_body:
                    msgs = err_body['response_status'].get('messages', [])
                    if msgs:
                        error_msg = "{0}: {1}".format(msgs[0].get('status_code'), msgs[0].get('message'))
            else:
                error_msg = err_body.get('error', error_msg)
        except ValueError:
            pass
    
    module.fail_json(msg=error_msg, status=info.get('status'), error_details=response_body)
