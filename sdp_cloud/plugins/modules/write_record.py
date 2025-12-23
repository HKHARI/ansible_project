# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: write_record
short_description: Write API module for ManageEngine ServiceDesk Plus Cloud
description:
  - Performs state-changing API operations (POST, PUT, DELETE) on ManageEngine ServiceDesk Plus Cloud entities.
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
    no_log: true
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
  operation:
    description:
      - The operation to perform.
    type: str
    default: Add
    choices: [Add, Update, Delete]
  payload:
    description:
      - The input data for the API request.
    type: dict
author:
  - Harish Kumar
'''

EXAMPLES = r'''
- name: Create a Request
  manageengine.sdp_cloud.write_record:
    domain: "sdpondemand.manageengine.com"
    parent_module_name: "request"
    client_id: "your_client_id"
    client_secret: "your_client_secret"
    refresh_token: "your_refresh_token"
    dc: "US"
    portal_name: "ithelpdesk"
    payload:
      subject: "New Request from Ansible"
      description: "Created via sdp_api_write module"
      requester: "Administrator"

- name: Update a Problem
  manageengine.sdp_cloud.write_record:
    domain: "sdpondemand.manageengine.com"
    parent_module_name: "problem"
    parent_id: "100"
    operation: "Update"
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
    run_write_module()

if __name__ == '__main__':
    main()
