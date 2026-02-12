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
  - Automatically infers the operation (Create vs Update) based on the presence of C(parent_id).
  - Use C(delete_record) module for deletions.
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
      - The parent module name (e.g., requests, problems, changes, releases).
    type: str
    required: true
    choices: [request, problem, change, release]
  parent_id:
    description:
      - The ID of the parent entity.
      - Required for Update operations.
    type: str
  payload:
    description:
      - The input data for the API request.
    type: dict
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.api_util import (
    SDPClient, common_argument_spec, validate_parameters, construct_endpoint,
    AUTH_MUTUALLY_EXCLUSIVE, AUTH_REQUIRED_TOGETHER
)
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.sdp_config import MODULE_CONFIG
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.udf_utils import is_udf_field, get_udf_field_type


def resolve_field_metadata(module, client, module_config, field_name):
    """
    Determine if a field is System or UDF and return its metadata.
    Returns: (field_type, category, group_name)
    category: 'system' or 'udf'
    """
    # 1. Check System Field Configuration
    system_fields = module_config.get('supported_system_field_meta', {})

    if field_name in system_fields:
        f_config = system_fields[field_name]
        return f_config.get('type'), 'system', f_config.get('group_name')

    # 2. Check UDF
    if is_udf_field(field_name):
        if not client:
            module.warn("UDF field '{0}' found but no client available. Treating as string.".format(field_name))
            return 'string', 'udf', None

        # Fetch UDF type from parent module metadata
        parent_module = module.params['parent_module_name']
        udf_type = get_udf_field_type(module, client, parent_module, field_name)
        return udf_type, 'udf', None

    # 3. Invalid Field
    return None, None, None


def transform_field_value(module, field_name, value, ftype):
    """
    Transform the value based on the resolved field type.
    """
    if ftype == 'string' or ftype == 'num' or ftype == 'bool':
        # For explicit bool types in config/UDF that want native bools
        if ftype == 'bool':
            if isinstance(value, str):
                return value.lower() == 'true'
            return bool(value)
        return value

    elif ftype == 'datetime':
        if not isinstance(value, (int, float)):
            module.fail_json(msg="Invalid datetime format for field '{0}'. value must be a timestamp (int/float).".format(field_name))
        return {'value': value}

    elif ftype == 'lookup':
        return {'name': value}

    elif ftype == 'user':
        if isinstance(value, str) and '@' in value:
            return {'email_id': value}
        return {'name': value}

    return value


def construct_payload(module, client=None):
    """
    Validate and construct the payload using a unified single-pass loop.
    """
    payload = module.params['payload']
    if not payload:
        return None

    parent_module = module.params['parent_module_name']

    # Fetch configuration
    module_config = MODULE_CONFIG.get(parent_module)

    # Root key for the payload wrapper
    root_key = parent_module

    # Initialize container with UDF section
    constructed_data = {'udf_fields': {}}

    for key, value in payload.items():
        # 1. Resolve Metadata
        ftype, category, group_name = resolve_field_metadata(module, client, module_config, key)

        if not category:
            # Invalid field
            allowed_fields = list(module_config.get('supported_system_field_meta', {}).keys())
            module.fail_json(msg="Invalid field '{0}'. Allowed system fields: {1}".format(key, allowed_fields))

        # 2. Transform Value
        final_value = transform_field_value(module, key, value, ftype)

        # 3. Placement Logic
        if category == 'system':
            if group_name:
                if group_name not in constructed_data:
                    constructed_data[group_name] = {}
                constructed_data[group_name][key] = final_value
            else:
                constructed_data[key] = final_value

        elif category == 'udf':
            constructed_data['udf_fields'][key] = final_value

    # Cleanup: Remove empty udf_fields if unused
    if not constructed_data['udf_fields']:
        del constructed_data['udf_fields']

    return {root_key: constructed_data}


def run_module():
    """Main execution entry point for write module."""
    module_args = common_argument_spec()
    module_args.update(dict(
        payload=dict(type='dict')
    ))

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False,
        mutually_exclusive=AUTH_MUTUALLY_EXCLUSIVE,
        required_together=AUTH_REQUIRED_TOGETHER
    )

    # Validation
    validate_parameters(module)

    client = SDPClient(module)
    endpoint = construct_endpoint(module)

    # Automatic Operation Inference
    parent_id = module.params.get('parent_id')

    method = 'POST'  # Default to Create

    # If parent_id is present, it's an Update
    if parent_id:
        method = 'PUT'

    # Construct Payload
    data = construct_payload(module, client)

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
