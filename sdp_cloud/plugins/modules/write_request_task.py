# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: write_request_task
short_description: Write Request Task for ManageEngine ServiceDesk Plus Cloud
description:
  - Creates or Updates Request Tasks in ServiceDesk Plus Cloud.
  - Automatically determines operation (Add/Update) based on presence of child_id.
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
  parent_id:
    description:
      - The Request ID (required).
    type: str
    required: true
  child_id:
    description:
      - The Task ID. If provided, the operation becomes an Update.
    type: str
  payload:
    description:
      - The input data for the Task.
    type: dict
  operation:
    description:
      - The operation to perform (Add, Update, Delete).
    type: str
    default: Add
    choices: [Add, Update, Delete]
  parent_module_name:
    description:
      - The parent module name (Internal Use).
    type: str
    choices: [request, problem, change]
  child_module_name:
    description:
      - The child module name (Internal Use).
    type: str
  grand_child_module_name:
    description:
      - The grandchild module name (Internal Use).
    type: str
  grand_child_id:
    description:
      - The grandchild ID (Internal Use).
    type: str
author:
  - Harish Kumar
'''

EXAMPLES = r'''
- name: Create a Request Task
  manageengine.sdp_cloud.write_request_task:
    domain: "sdpondemand.manageengine.com"
    parent_id: "100"
    client_id: "your_client_id"
    client_secret: "your_client_secret"
    refresh_token: "your_refresh_token"
    dc: "US"
    portal_name: "ithelpdesk"
    payload:
      title: "New Task"
      description: "Task Description"
      status: "Open"

- name: Update a Request Task
  manageengine.sdp_cloud.write_request_task:
    domain: "sdpondemand.manageengine.com"
    parent_id: "100"
    child_id: "201"
    client_id: "your_client_id"
    client_secret: "your_client_secret"
    refresh_token: "your_refresh_token"
    dc: "US"
    portal_name: "ithelpdesk"
    payload:
      status: "Closed"
'''

RETURN = r'''
response:
  description: The raw response from the SDP Cloud API.
  returned: always
  type: dict
'''

from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.write_utils import run_write_module

def main():
    run_write_module(module_name='request', child_module_name='task')

if __name__ == '__main__':
    main()
