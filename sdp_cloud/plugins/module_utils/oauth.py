# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
from ansible.module_utils.urls import fetch_url
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.sdp_config import DC_MAP

try:
    import urllib.parse as urllib_parse
except ImportError:
    import urllib
    urllib_parse = urllib


def get_access_token(module, client_id, client_secret, refresh_token, dc):
    """
    Generate Access Token using Refresh Token.
    Returns the full JSON response from the token endpoint.
    """
    accounts_url = DC_MAP.get(dc)
    if not accounts_url:
        module.fail_json(msg="Invalid DC provided: {0}".format(dc))

    token_url = "{0}/oauth/v2/token".format(accounts_url)

    payload_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    payload = urllib_parse.urlencode(payload_data)

    response, info = fetch_url(
        module,
        token_url,
        data=payload,
        method='POST',
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    if not response:
        _handle_error(module, info, "Failed to generate Access Token")

    try:
        data = json.loads(response.read())
        if 'access_token' in data:
            return data
        if 'error' in data:
            module.fail_json(msg="OAuth Error: {0}".format(data.get('error')), details=data)
    except ValueError:
        module.fail_json(msg="Invalid JSON response from Auth Server")

    module.fail_json(msg="Unknown error during token generation", response=data)


def _handle_error(module, info, default_msg):
    error_msg = info.get('msg', default_msg)
    if 'body' in info:
        try:
            err_body = json.loads(info['body'])
            # SDP Cloud V3 API Error Structure
            if 'response_status' in err_body:
                msgs = err_body['response_status'].get('messages', [])
                if msgs:
                    error_msg = "{0}: {1}".format(msgs[0].get('status_code'), msgs[0].get('message'))
            else:
                error_msg = err_body.get('error', error_msg)
        except ValueError:
            pass
    module.fail_json(msg=error_msg, status=info['status'])
