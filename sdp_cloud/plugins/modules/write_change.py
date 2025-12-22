# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: write_change_record
short_description: Write Change Record for ManageEngine ServiceDesk Plus Cloud
description:
  - Creates or Updates Change records in ServiceDesk Plus Cloud.
  - Automatically determines operation (Add/Update) based on presence of parent_id.
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
      - The Change ID. If provided, the operation becomes an Update.
    type: str
  payload:
    description:
      - The input data for the Change.
    type: dict
author:
  - Harish Kumar <@HKHARI>
'''

EXAMPLES = r'''
- name: Create a Change
  manageengine.sdp_cloud.write_change_record:
    domain: "sdpondemand.manageengine.com"
    client_id: "your_client_id"
    client_secret: "your_client_secret"
    refresh_token: "your_refresh_token"
    dc: "US"
    portal_name: "ithelpdesk"
    payload:
      title: "New Change"
      description: "Description"

- name: Update a Change
  manageengine.sdp_cloud.write_change_record:
    domain: "sdpondemand.manageengine.com"
    parent_id: "100"
    client_id: "your_client_id"
    client_secret: "your_client_secret"
    refresh_token: "your_refresh_token"
    dc: "US"
    portal_name: "ithelpdesk"
    payload:
      title: "Updated Title"
'''

RETURN = r'''
response:
  description: The raw response from the SDP Cloud API.
  returned: always
  type: dict
'''

from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.write_utils import run_write_module

def main():
    run_write_module(module_name='change')

if __name__ == '__main__':
    main()
