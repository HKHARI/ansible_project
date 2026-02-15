# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


def _is_valid_email(value):
    """Return True if value looks like an email (local@domain.tld). Rejects e.g. 'hell@hi'."""
    if not isinstance(value, str) or not value:
        return False
    parts = value.split('@')
    if len(parts) != 2:
        return False
    local, domain = parts
    if not local or not domain:
        return False
    # Domain must contain at least one dot (e.g. example.com)
    if '.' not in domain:
        return False
    return True


DOCUMENTATION = r'''
---
module: write_record
author:
  - Harish Kumar (@harishkumar-k-7052)
short_description: Manage records in ManageEngine ServiceDesk Plus Cloud
description:
  - Creates, updates, or deletes entities in ManageEngine ServiceDesk Plus Cloud.
  - When C(state=present) (default), automatically infers create vs update based on the presence of C(parent_id).
  - When C(state=absent), deletes the record identified by C(parent_id).
  - Supports idempotency, check mode, and diff mode.
extends_documentation_fragment:
  - manageengine.sdp_cloud.sdp
options:
  state:
    description:
      - The desired state of the record.
      - C(present) ensures the record exists (create or update).
      - C(absent) ensures the record is deleted.
    type: str
    default: present
    choices: [present, absent]
  payload:
    description:
      - The input data for the API request.
      - For create operations, this should contain the fields for the new record.
      - For update operations, this should contain only the fields to be modified.
      - Not used when C(state=absent).
    type: dict
'''

EXAMPLES = r'''
- name: Create a Request
  manageengine.sdp_cloud.write_record:
    domain: "sdpondemand.manageengine.com"
    parent_module_name: "request"
    state: present
    client_id: "your_client_id"
    client_secret: "your_client_secret"
    refresh_token: "your_refresh_token"
    dc: "US"
    portal_name: "ithelpdesk"
    payload:
      subject: "New Request from Ansible"
      description: "Created via sdp_api_write module"
      requester: "requester@example.com"

- name: Update a Problem
  manageengine.sdp_cloud.write_record:
    domain: "sdpondemand.manageengine.com"
    parent_module_name: "problem"
    parent_id: "100"
    state: present
    client_id: "your_client_id"
    client_secret: "your_client_secret"
    refresh_token: "your_refresh_token"
    dc: "US"
    portal_name: "ithelpdesk"
    payload:
      title: "Updated Title"

- name: Delete a Request
  manageengine.sdp_cloud.write_record:
    domain: "sdpondemand.manageengine.com"
    parent_module_name: "request"
    parent_id: "100"
    state: absent
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
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.api_util import (
    SDPClient, common_argument_spec, check_module_config, construct_endpoint,
    get_current_record, has_differences,
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
        # User fields accept only a valid email_id (local@domain.tld), not e.g. 'hell@hi' or a name.
        if not _is_valid_email(value):
            module.fail_json(
                msg="User field '{0}' accepts only a valid email address (e.g. user@example.com). Got: {1}".format(field_name, value)
            )
        return {'email_id': value}

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


def _handle_absent(module, client, endpoint, parent_module):
    """Handle state=absent (delete) logic."""
    parent_id = module.params.get('parent_id')

    if not parent_id:
        module.fail_json(msg="parent_id is required when state=absent.")

    # Idempotency: Check if the record exists before attempting delete
    current_record = get_current_record(client, module)

    if not current_record:
        module.exit_json(changed=False, msg="Record does not exist, nothing to delete.")

    if module.check_mode:
        result = dict(
            changed=True,
            msg="Would delete {0} record with id {1}.".format(parent_module, parent_id),
        )
        if module._diff:
            result['diff'] = {'before': current_record, 'after': {}}
        module.exit_json(**result)

    response = client.request(endpoint=endpoint, method='DELETE')

    result = dict(changed=True, response=response)
    if module._diff:
        result['diff'] = {'before': current_record, 'after': {}}
    module.exit_json(**result)


def _handle_present(module, client, endpoint, parent_module):
    """Handle state=present (create/update) logic."""
    parent_id = module.params.get('parent_id')

    method = 'PUT' if parent_id else 'POST'

    # Construct Payload
    data = construct_payload(module, client)

    # Idempotency: For updates, compare desired state with current state
    current_record = None
    if method == 'PUT' and data:
        current_record = get_current_record(client, module)

        if current_record and not has_differences(data, current_record, parent_module):
            # No changes needed -- exit without making the API call
            module.exit_json(changed=False, response={parent_module: current_record}, payload=data)

    # Check mode: report what would change without making the API call
    if module.check_mode:
        result = dict(
            changed=True,
            msg="Would {0} a {1} record.".format('update' if method == 'PUT' else 'create', parent_module),
            payload=data,
        )
        if module._diff and current_record:
            result['diff'] = {'before': current_record, 'after': data.get(parent_module, {})}
        module.exit_json(**result)

    response = client.request(endpoint=endpoint, method=method, data=data)

    result = dict(changed=True, response=response, payload=data, endpoint=endpoint, method=method)

    if module._diff:
        result['diff'] = {
            'before': current_record or {},
            'after': response.get(parent_module, {})
        }

    module.exit_json(**result)


def run_module():
    """Main execution entry point for write module."""
    module_args = common_argument_spec()
    module_args.update(dict(
        state=dict(type='str', default='present', choices=['present', 'absent']),
        payload=dict(type='dict'),
    ))

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=AUTH_MUTUALLY_EXCLUSIVE,
        required_together=AUTH_REQUIRED_TOGETHER
    )

    # Validation
    check_module_config(module)

    client = SDPClient(module)
    endpoint = construct_endpoint(module)
    parent_module = module.params['parent_module_name']
    state = module.params['state']

    if state == 'absent':
        _handle_absent(module, client, endpoint, parent_module)
    else:
        _handle_present(module, client, endpoint, parent_module)


def main():
    run_module()


if __name__ == '__main__':
    main()
