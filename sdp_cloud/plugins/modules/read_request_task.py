# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: read_request_task
short_description: Read Request Task for ManageEngine ServiceDesk Plus Cloud
description:
  - Retrieves Request Task details or a list of Tasks for a Request.
extends_documentation_fragment:
  - manageengine.sdp_cloud.sdp
options:
  domain:
    description:
      - The domain URL of your ServiceDesk Plus Cloud instance.
    type: str
    required: true
  portal_name:
    description:
      - The portal name.
    type: str
    required: true
  auth_token:
    description:
      - The OAuth access token.
      - Mutually exclusive with I(client_id), I(client_secret), I(refresh_token).
    type: str
    no_log: true
  parent_id:
    description:
      - The Request ID (required).
    type: str
    required: true
  child_id:
    description:
      - The Task ID. If provided, fetches details for this specific Task.
    type: str
  payload:
    description:
      - The input data for filtering the list of Tasks (e.g., row_count, start_index).
    type: dict
author:
  - Harish Kumar <@HKHARI>
'''

EXAMPLES = r'''
- name: Get Request Task Details
  manageengine.sdp_cloud.read_request_task:
    domain: "sdpondemand.manageengine.com"
    parent_id: "100"
    child_id: "201"
    client_id: "your_client_id"
    client_secret: "your_client_secret"
    refresh_token: "your_refresh_token"
    dc: "US"
    portal_name: "ithelpdesk"

- name: Get List of Request Tasks
  manageengine.sdp_cloud.read_request_task:
    domain: "sdpondemand.manageengine.com"
    parent_id: "100"
    client_id: "your_client_id"
    client_secret: "your_client_secret"
    refresh_token: "your_refresh_token"
    dc: "US"
    portal_name: "ithelpdesk"
    payload:
      row_count: 10
'''

RETURN = r'''
response:
  description: The raw response from the SDP Cloud API.
  returned: always
  type: dict
'''

from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.read_utils import run_read_module

def main():
    run_read_module(module_name='request', child_module_name='task')

if __name__ == '__main__':
    main()
