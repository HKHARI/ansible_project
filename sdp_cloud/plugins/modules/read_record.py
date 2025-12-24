# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: read_record
short_description: Read API module for ManageEngine ServiceDesk Plus Cloud
description:
  - Performs data retrieval API operations (GET) on ManageEngine ServiceDesk Plus Cloud entities.
  - Supports Requests, Problems, and Changes.
  - Supports Parent, Child, and Grandchild module hierarchy.
extends_documentation_fragment:
  - manageengine.sdp_cloud.sdp
options:
  domain:
    description:
      - The domain URL of your ServiceDesk Plus Cloud instance (e.g., sdpondemand.manageengine.com).
    type: str
    required: true
  portal_name:
    description:
      - The portal name (e.g., ithelpdesk).
    type: str
    required: true
  auth_token:
    description:
      - The OAuth access token.
      - Mutually exclusive with I(client_id), I(client_secret), I(refresh_token).
    type: str
  parent_module_name:
    description:
      - The parent module name (e.g., requests, problems, changes).
    type: str
    required: true
    choices: [request, problem, change]
  child_module_name:
    description:
      - The child module name (e.g., tasks, worklog, uploads, checklists).
    type: str
  grand_child_module_name:
    description:
      - The grandchild module name (e.g., comments, worklogs, uploads).
    type: str
  parent_id:
    description:
      - The ID of the parent entity.
    type: str
  child_id:
    description:
      - The ID of the child entity.
    type: str
  grand_child_id:
    description:
      - The ID of the grandchild entity.
    type: str
  payload:
    description:
      - The input data for the API request (e.g., list_info parameters like row_count, start_index).
    type: dict
author:
  - Harish Kumar
'''

EXAMPLES = r'''
- name: Get Request Details
  manageengine.sdp_cloud.read_record:
    domain: "sdpondemand.manageengine.com"
    parent_module_name: "request"
    parent_id: "100"
    client_id: "your_client_id"
    client_secret: "your_client_secret"
    refresh_token: "your_refresh_token"
    dc: "US"
    portal_name: "ithelpdesk"

- name: Get List of Requests
  manageengine.sdp_cloud.read_record:
    domain: "sdpondemand.manageengine.com"
    parent_module_name: "request"
    client_id: "your_client_id"
    client_secret: "your_client_secret"
    refresh_token: "your_refresh_token"
    dc: "US"
    portal_name: "ithelpdesk"
    payload:
      row_count: 10
      start_index: 1
'''

RETURN = r'''
response:
  description: The raw response from the SDP Cloud API.
  returned: always
  type: dict
'''

from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.read_utils import run_read_module

def main():
    run_read_module()


if __name__ == '__main__':
    main()
