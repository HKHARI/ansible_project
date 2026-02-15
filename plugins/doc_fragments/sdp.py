# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    # Standard documentation fragment for all SDP Cloud modules
    DOCUMENTATION = r'''
options:
  domain:
    description:
      - The domain URL of your ServiceDesk Plus Cloud instance.
      - For example, C(sdpondemand.manageengine.com) or C(sdp.zoho.eu).
    type: str
    required: true
  portal_name:
    description:
      - The portal name of your ServiceDesk Plus Cloud instance (e.g., C(ithelpdesk)).
    type: str
    required: true
  auth_token:
    description:
      - The OAuth access token for authenticating API requests.
      - Mutually exclusive with I(client_id), I(client_secret), and I(refresh_token).
    type: str
  parent_module_name:
    description:
      - The ITSM module to operate on.
    type: str
    required: true
    choices: [request, problem, change, release]
  parent_id:
    description:
      - The ID of the specific record to operate on.
      - Required for update, get-by-id, and delete operations.
    type: str
'''
