# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: sdp_api
short_description: Generic API module for ManageEngine ServiceDesk Plus Cloud
description:
  - Performs generic API operations on ManageEngine ServiceDesk Plus Cloud entities.
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
    choices: [requests, problems, changes]
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
  method:
    description:
      - The HTTP method to use.
    type: str
    default: POST
    choices: [GET, POST, PUT, DELETE]
  payload:
    description:
      - The input data for the API request.
    type: dict
author:
  - Harish Kumar <@HKHARI>
'''

EXAMPLES = r'''
- name: Create a Request
  manageengine.sdp_cloud.sdp_api:
    domain: "sdpondemand.manageengine.com"
    parent_module_name: "requests"
    client_id: "your_client_id"
    client_secret: "your_client_secret"
    refresh_token: "your_refresh_token"
    dc: "US"
    portal_name: "ithelpdesk"
    payload:
      subject: "New Request from Ansible"
      description: "Created via sdp_api module"
      requester: "Administrator"

- name: Get Request Details
  manageengine.sdp_cloud.sdp_api:
    domain: "sdpondemand.manageengine.com"
    parent_module_name: "requests"
    parent_id: "100"
    method: "GET"
    client_id: "your_client_id"
    client_secret: "your_client_secret"
    refresh_token: "your_refresh_token"
    dc: "US"
    portal_name: "ithelpdesk"
'''

RETURN = r'''
response:
  description: The raw response from the SDP Cloud API.
  returned: always
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.sdp_api import SDPClient
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.sdp_config import MODULE_CONFIG
import re

# Dummy imports to force Ansible to bundle these module_utils files
if False:
    from ansible_collections.manageengine.sdp_cloud.plugins.module_utils import requests_fields_config
    from ansible_collections.manageengine.sdp_cloud.plugins.module_utils import problems_fields_config

def load_field_config(module, module_name):
    """Dynamically load field configuration for the given module."""
    config_module_name = "ansible_collections.manageengine.sdp_cloud.plugins.module_utils.{0}_fields_config".format(module_name)
    try:
        # Use __import__ for dynamic loading compatible with Ansible's module loader
        mod = __import__(config_module_name, fromlist=['ALLOWED_PAYLOAD_FIELDS', 'FIELD_TYPE_CONFIG'])
        module.debug("Successfully loaded config for {0}".format(module_name))
        return mod.ALLOWED_PAYLOAD_FIELDS, mod.FIELD_TYPE_CONFIG
    except ImportError as e:
        module.fail_json(msg="Unsupported module '{0}' or missing configuration file. Error: {1}".format(module_name, str(e)))
        return None, None # Unreachable


def validate_parameters(module):
    """Validate parameter dependencies."""
    parent_id = module.params['parent_id']
    child_id = module.params['child_id']
    grand_child_id = module.params['grand_child_id']
    child_module = module.params['child_module_name']
    grand_child_module = module.params['grand_child_module_name']
    parent_module = module.params['parent_module_name']

    if child_id and not parent_id:
        module.fail_json(msg="parent_id is required when child_id is provided.")
    
    if grand_child_id and not (child_id and parent_id):
        module.fail_json(msg="parent_id and child_id are required when grand_child_id is provided.")

    if child_module and not parent_id:
         module.fail_json(msg="parent_id is required when child_module_name is provided.")

    if grand_child_module and not (child_module and child_id and parent_id):
        module.fail_json(msg="parent_id, child_module_name, and child_id are required when grand_child_module_name is provided.")


def construct_endpoint(module):
    """Construct the API endpoint based on hierarchy."""
    parent_module = module.params['parent_module_name']
    parent_id = module.params['parent_id']
    child_module = module.params['child_module_name']
    child_id = module.params['child_id']
    grand_child_module = module.params['grand_child_module_name']
    grand_child_id = module.params['grand_child_id']

    endpoint = parent_module
    
    if parent_id:
        endpoint += "/{0}".format(parent_id)
        
        if child_module:
            endpoint += "/{0}".format(child_module)
            
            if child_id:
                endpoint += "/{0}".format(child_id)
                
                if grand_child_module:
                    endpoint += "/{0}".format(grand_child_module)
                    
                    if grand_child_id:
                        endpoint += "/{0}".format(grand_child_id)
    
    return endpoint

def construct_payload(module):
    """Validate and construct the payload."""
    payload = module.params['payload']
    if not payload:
        return None

    parent_module = module.params['parent_module_name']
    
    allowed_fields, field_types = load_field_config(module, parent_module)
    
    new_payload = {}
    
    for key, value in payload.items():
        if key not in allowed_fields:
            module.fail_json(msg="Field '{0}' is not allowed for module '{1}'. Allowed fields: {2}".format(key, parent_module, allowed_fields))
        
        # Strict Type Validation: Value cannot be a dict
        if isinstance(value, dict):
            module.fail_json(msg="Field '{0}' has invalid type 'dict'. Only String, Number, and Boolean are allowed.".format(key))

        field_config = field_types.get(key)
        field_type = field_config.get('type') if field_config else 'string'
        
        module.debug("Processing field '{0}' with type '{1}'".format(key, field_type))

        # 1. Process Value based on Type
        processed_value = value
        
        if field_type == 'lookup':
            # User provides name
            processed_value = {"name": value}
        elif field_type == 'user':
            # User provides name or email
            # Simple regex for email validation
            email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
            if re.match(email_regex, str(value)):
                processed_value = {"email_id": value}
            else:
                processed_value = {"name": value}
        elif field_type == 'boolean':
            processed_value = str(value).lower()
        elif field_type == 'datetime':
             # Validate and process datetime
             if isinstance(value, bool):
                 module.fail_json(msg="Field '{0}' of type 'datetime' cannot be a boolean.".format(key))
             
             if isinstance(value, (int, float)):
                 val_str = str(int(value))
             else:
                 val_str = str(value).strip()
             
             if not val_str:
                  module.fail_json(msg="Field '{0}' of type 'datetime' cannot be empty.".format(key))

             if val_str.isdigit():
                 processed_value = {"value": val_str}
             else:
                 processed_value = {"display_value": val_str}
        #Handle Grouping
        if field_config and field_config.get('is_group_field'):
            group_name = field_config.get('group_name')
            if group_name:
                if group_name not in new_payload:
                    new_payload[group_name] = {}
                new_payload[group_name][key] = processed_value
            else:
                new_payload[key] = processed_value
        else:
            new_payload[key] = processed_value
    
    # Wrap in module singular name
    config = MODULE_CONFIG.get(parent_module)
    if config:
        singular = config['singular']
        return {singular: new_payload}
        
    return new_payload


def run_module():
    module_args = dict(
        domain=dict(type='str', required=True),
        portal_name=dict(type='str', required=True),
        auth_token=dict(type='str', no_log=True),
        client_id=dict(type='str'),
        client_secret=dict(type='str', no_log=True),
        refresh_token=dict(type='str', no_log=True),
        dc=dict(type='str', required=True, choices=['US', 'EU', 'IN', 'AU', 'CN', 'JP', 'CA', 'SA']),
        
        parent_module_name=dict(type='str', required=True, choices=['requests', 'problems', 'changes']),
        child_module_name=dict(type='str'),
        grand_child_module_name=dict(type='str'),
        
        parent_id=dict(type='str'),
        child_id=dict(type='str'),
        grand_child_id=dict(type='str'),
        
        method=dict(type='str', default='POST', choices=['GET', 'POST', 'PUT', 'DELETE']),
        payload=dict(type='dict')
    )

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
    
    method = module.params['method']
    
    # Construct Payload
    data = None
    
    if method in ['POST', 'PUT']:
        data = construct_payload(module)
    elif method == 'GET' and module.params['payload']:
        payload = module.params['payload']
        data = {"list_info": payload}

    response = client.request(
        endpoint=endpoint,
        method=method,
        data=data
    )

    module.exit_json(changed=True, response=response, payload=data)


def main():
    run_module()


if __name__ == '__main__':
    main()
