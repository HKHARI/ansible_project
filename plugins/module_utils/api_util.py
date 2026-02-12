# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
from ansible.module_utils.urls import fetch_url
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.oauth import get_access_token
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.sdp_config import DC_CHOICES, MODULE_CONFIG

from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.error_handler import handle_error
try:
    import urllib.parse as urllib_parse
except ImportError:
    import urllib
    urllib_parse = urllib


# Auth Constants
AUTH_MUTUALLY_EXCLUSIVE = [
    ('auth_token', 'client_id'),
    ('auth_token', 'client_secret'),
    ('auth_token', 'refresh_token')
]

AUTH_REQUIRED_TOGETHER = [
    ('client_id', 'client_secret', 'refresh_token')
]


def common_argument_spec():
    """Return common argument specification for SDP modules."""
    return dict(
        domain=dict(type='str', required=True),
        portal_name=dict(type='str', required=True),
        auth_token=dict(type='str', no_log=True),
        client_id=dict(type='str'),
        client_secret=dict(type='str', no_log=True),
        refresh_token=dict(type='str', no_log=True),
        dc=dict(type='str', required=True, choices=DC_CHOICES),
        parent_module_name=dict(type='str', required=True, choices=list(MODULE_CONFIG.keys())),
        parent_id=dict(type='str'),
    )


def validate_parameters(module):
    """Validate parameter dependencies and hierarchy."""
    parent_module = module.params['parent_module_name']

    # Hierarchy Validation
    parent_config = MODULE_CONFIG.get(parent_module)
    if not parent_config:
        module.fail_json(msg="Invalid parent_module_name: {0}".format(parent_module))

    return True


def construct_endpoint(module, operation=None):
    """Construct the API endpoint based on hierarchy."""
    parent_module = module.params['parent_module_name']
    parent_id = module.params.get('parent_id')

    # Get endpoints from config
    parent_config = MODULE_CONFIG.get(parent_module)
    endpoint = parent_config['endpoint']

    if parent_id:
        endpoint += "/{0}".format(parent_id)

    # Append convenience operation at the deepest level
    if operation:
        endpoint += "/{0}".format(operation)

    return endpoint


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
                self.module.fail_json(msg="Missing authentication credentials. Provide either 'auth_token' or "
                                      "('client_id', 'client_secret', 'refresh_token').")

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

        status_code = info.get('status', -1)

        # On HTTP error, fetch_url sets response=None but puts error body in info['body']
        if not response:
            error_body = info.get('body', '')
            if error_body:
                try:
                    err_json = json.loads(error_body)
                    # Return the parsed error so callers can inspect it
                    handle_error(self.module, info, "API Request Failed")
                except ValueError:
                    handle_error(self.module, info, "API Request Failed")
            else:
                handle_error(self.module, info, "API Request Failed")

        body = response.read()
        if not body:
            return {"status": status_code, "msg": "Empty response body"}

        try:
            result = json.loads(body)
        except ValueError:
            self.module.fail_json(msg="Invalid JSON response from SDP API", raw_response=body)

        # Check for API-level errors even on HTTP 200
        if isinstance(result, dict):
            resp_status = result.get('response_status', {})
            if isinstance(resp_status, dict) and resp_status.get('status_code', 2000) >= 4000:
                self.module.fail_json(
                    msg="{0}".format(resp_status.get('messages', [{}])[0].get('message', 'API Error')),
                    status=resp_status.get('status_code'),
                    response=result
                )

        return result






