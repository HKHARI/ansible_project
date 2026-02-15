# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: oauth_token
author:
  - Harish Kumar (@harishkumar-k-7052)
short_description: Generate ManageEngine SDP Cloud OAuth Access Token
description:
  - Generates a temporary OAuth access token using a refresh token.
  - This token is required for authenticating against the ServiceDesk Plus Cloud API.
  - The access token is valid for 1 hour.
extends_documentation_fragment:
  - manageengine.sdp_cloud.auth
options:
  client_id:
    description:
      - The Client ID generated from the Zoho API Console.
    type: str
    required: true
  client_secret:
    description:
      - The Client Secret generated from the Zoho API Console.
    type: str
    required: true
  refresh_token:
    description:
      - The long-lived refresh token.
    type: str
    required: true
'''

EXAMPLES = r'''
- name: Generate Access Token using Vaulted Variables
  manageengine.sdp_cloud.oauth_token:
    client_id: "{{ sdp_client_id }}"
    client_secret: "{{ sdp_client_secret }}"
    refresh_token: "{{ sdp_refresh_token }}"
    dc: "US"
  register: auth_response
  no_log: true

- name: Use the token in subsequent tasks
  manageengine.sdp_cloud.read_record:
    domain: "sdpondemand.manageengine.com"
    portal_name: "ithelpdesk"
    parent_module_name: "request"
    parent_id: "100"
    auth_token: "{{ auth_response.access_token }}"
    dc: "US"
'''

RETURN = r'''
access_token:
  description: The short-lived OAuth access token.
  returned: always
  type: str
expires_in:
  description: The duration in seconds until the access token expires (usually 3600).
  returned: always
  type: int
token_type:
  description: The type of token (e.g., Bearer).
  returned: always
  type: str
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.oauth import get_access_token


def run_module():
    module_args = dict(
        client_id=dict(type='str', required=True),
        client_secret=dict(type='str', required=True, no_log=True),
        refresh_token=dict(type='str', required=True, no_log=True),
        dc=dict(type='str', required=True, choices=['US', 'EU', 'IN', 'AU', 'CN', 'JP', 'CA', 'SA'])
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    client_id = module.params['client_id']
    client_secret = module.params['client_secret']
    refresh_token = module.params['refresh_token']
    dc = module.params['dc']

    data = get_access_token(module, client_id, client_secret, refresh_token, dc)

    module.exit_json(
        changed=False,
        access_token=data['access_token'],
        expires_in=int(data.get('expires_in')) if data.get('expires_in') is not None else None,
        token_type=data.get('token_type')
    )


def main():
    run_module()


if __name__ == '__main__':
    main()
