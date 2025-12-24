# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    # Standard documentation fragment
    DOCUMENTATION = r'''
options:
  client_id:
    description:
      - The Client ID generated from the Zoho API Console.
    type: str
  client_secret:
    description:
      - The Client Secret generated from the Zoho API Console.
    type: str

  refresh_token:
    description:
      - The long-lived refresh token.
    type: str

  dc:
    description:
      - The Data Center location (e.g., US, EU).
    type: str
    choices: [US, EU, IN, AU, CN, JP, CA, SA]
'''
