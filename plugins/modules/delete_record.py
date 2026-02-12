# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: delete_record
short_description: Delete API module for ManageEngine ServiceDesk Plus Cloud
description:
  - This module deletes records in ManageEngine ServiceDesk Plus Cloud.
  - It handles HTTP DELETE requests for specified modules and IDs.
author:
  - Harish Kumar (@HKHARI)
options:
  domain:
    description:
      - The domain of the SDP Cloud instance (e.g., sdpondemand.manageengine.com, sdp.zoho.eu).
    required: true
    type: str
  parent_module_name:
    description:
      - The name of the parent module.
    required: true
    type: str
    choices: [request, problem, change, release]
  parent_id:
    description:
      - The ID of the record to delete.
    type: str
    required: true
  client_id:
    description:
      - The OAuth Client ID.
      - Required if I(auth_token) is not provided.
    type: str
  client_secret:
    description:
      - The OAuth Client Secret.
      - Required if I(auth_token) is not provided.
    type: str
  refresh_token:
    description:
      - The OAuth Refresh Token.
      - Required if I(auth_token) is not provided.
    type: str
  auth_token:
    description:
      - The OAuth Access Token.
      - Required if I(client_id), I(client_secret), and I(refresh_token) are not provided.
    type: str
  dc:
    description:
      - The Data Center location (e.g., US, EU).
    type: str
    required: true
    choices: [US, EU, IN, AU, CN, JP, CA, SA]
  portal_name:
    description:
      - The portal name (e.g., ithelpdesk).
    type: str
    required: true
extends_documentation_fragment:
  - manageengine.sdp_cloud.sdp
'''

EXAMPLES = r'''
- name: Delete a Problem
  manageengine.sdp_cloud.delete_record:
    domain: "sdpondemand.manageengine.com"
    parent_module_name: "problem"
    parent_id: "100"
    client_id: "your_client_id"
    client_secret: "your_client_secret"
    refresh_token: "your_refresh_token"
    dc: "US"
    portal_name: "ithelpdesk"
'''

RETURN = r'''
response:
  description: The full response from the API.
  returned: always
  type: dict
  sample:
    response_status:
      status: "success"
      status_code: 2000
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.api_util import (
    SDPClient, common_argument_spec, validate_parameters, construct_endpoint,
    AUTH_MUTUALLY_EXCLUSIVE, AUTH_REQUIRED_TOGETHER
)


def run_delete_module():
    """Main execution function for delete module."""
    module_args = common_argument_spec()

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False,
        mutually_exclusive=AUTH_MUTUALLY_EXCLUSIVE,
        required_together=AUTH_REQUIRED_TOGETHER
    )

    # Validation
    validate_parameters(module)

    # Strict check for ID presence because DELETE requires an ID
    parent_id = module.params.get('parent_id')

    if not parent_id:
        module.fail_json(msg="parent_id is required for deletion.")

    client = SDPClient(module)
    endpoint = construct_endpoint(module)
    method = 'DELETE'

    response = client.request(
        endpoint=endpoint,
        method=method
    )

    module.exit_json(changed=True, response=response)


def main():
    run_delete_module()


if __name__ == '__main__':
    main()
