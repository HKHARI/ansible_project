# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: write_record
author:
  - Harish Kumar (@HKHARI)
short_description: Write API module for ManageEngine ServiceDesk Plus Cloud
description:
  - Creates or updates entities in ManageEngine ServiceDesk Plus Cloud.
  - Automatically infers the operation (Create vs Update) based on the presence of `parent_id` (and `child_id` for child modules).
  - Use `delete_record` module for deletions.
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
  dc:
    description:
      - The Data Center location (e.g., US, EU).
    type: str
    required: true
    choices: [US, EU, IN, AU, CN, JP, CA, SA]
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
  parent_id:
    description:
      - The ID of the parent entity.
      - Required for Update operations on parent records.
    type: str
  child_id:
    description:
      - The ID of the child entity.
      - Required for Update operations on child entities.
    type: str
  payload:
    description:
      - The input data for the API request.
    type: dict
    required: true
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
