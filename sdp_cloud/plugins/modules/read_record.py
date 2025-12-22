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
  grand_child_id:
    description:
      - The ID of the grandchild entity.
    type: str
  payload:
    description:
      - The input data for the API request (e.g., list_info parameters like row_count, start_index).
    type: dict
author:
  - Harish Kumar <@HKHARI>
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.api_util import SDPClient, common_argument_spec, validate_parameters, construct_endpoint


def load_field_config(module, module_name, child_module=None):
    """Dynamically load field configuration for the given module."""
    if child_module:
        config_name = "{0}_{1}_fields_config".format(module_name, child_module)
    else:
        config_name = "{0}_fields_config".format(module_name)
        
    config_module_name = "ansible_collections.manageengine.sdp_cloud.plugins.module_utils.field_conf.{0}".format(config_name)
    try:
        # Use __import__ for dynamic loading compatible with Ansible's module loader
        mod = __import__(config_module_name, fromlist=['ALLOWED_SORT_FIELDS'])
        module.debug("Successfully loaded config for {0}".format(config_name))
        return mod.ALLOWED_SORT_FIELDS
    except ImportError as e:
        module.fail_json(msg="Unsupported module '{0}' or missing configuration file. Error: {1}".format(config_name, str(e)))
        return None # Unreachable


def construct_payload(module):
    """Validate and construct the payload."""
    payload = module.params['payload']
    if not payload:
        return None

    parent_module = module.params['parent_module_name']
    child_module = module.params['child_module_name']
    
    # Load allowed sort fields
    allowed_sort_fields = load_field_config(module, parent_module, child_module)
    
    validated_payload = {}
    
    # Allowed keys for list_info
    allowed_keys = ['row_count', 'sort_field', 'sort_order', 'get_total_count']
    
    for key in payload.keys():
        if key not in allowed_keys:
            module.fail_json(msg="Invalid payload key '{0}'. Allowed keys: {1}".format(key, allowed_keys))

    # 1. row_count
    row_count = payload.get('row_count', 10)
    try:
        row_count = int(row_count)
    except ValueError:
        module.fail_json(msg="row_count must be an integer.")
        
    if not (1 <= row_count <= 100):
        module.fail_json(msg="row_count must be between 1 and 100.")
    validated_payload['row_count'] = row_count

    # 2. sort_field
    sort_field = payload.get('sort_field', 'created_date')
    if sort_field not in allowed_sort_fields:
        module.fail_json(msg="Invalid sort_field '{0}'. Allowed fields: {1}".format(sort_field, allowed_sort_fields))
    validated_payload['sort_field'] = sort_field

    # 3. sort_order
    sort_order = payload.get('sort_order', 'asc')
    if sort_order not in ['asc', 'desc']:
        module.fail_json(msg="Invalid sort_order '{0}'. Allowed values: ['asc', 'desc']".format(sort_order))
    validated_payload['sort_order'] = sort_order

    # 4. get_total_count
    get_total_count = payload.get('get_total_count', False)
    if isinstance(get_total_count, str):
        if get_total_count.lower() == 'true':
            get_total_count = True
        elif get_total_count.lower() == 'false':
            get_total_count = False
        else:
             module.fail_json(msg="get_total_count must be a boolean.")
    elif not isinstance(get_total_count, bool):
         module.fail_json(msg="get_total_count must be a boolean.")
    
    validated_payload['get_total_count'] = get_total_count

    return {"list_info": validated_payload}


def run_module():
    # Get common arguments
    module_args = common_argument_spec()
    
    # Add/Override module specific arguments
    module_args.update(dict(
        payload=dict(type='dict')
    ))

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False,
        mutually_exclusive=[
            ('auth_token', 'client_id'),
            ('auth_token', 'client_secret'),
            ('auth_token', 'refresh_token')
        ],
        required_together=[
            ('client_id', 'client_secret', 'refresh_token')
        ]
    )

    validate_parameters(module)

    client = SDPClient(module)
    
    endpoint = construct_endpoint(module)
    
    # Construct Payload
    data = construct_payload(module)

    response = client.request(
        endpoint=endpoint,
        method='GET',
        data=data
    )

    module.exit_json(changed=False, response=response, payload=data)


def main():
    run_module()


if __name__ == '__main__':
    main()
