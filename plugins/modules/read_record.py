# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: read_record
author:
  - Harish Kumar (@HKHARI)
short_description: Read API module for ManageEngine ServiceDesk Plus Cloud
description:
  - Performs data retrieval API operations (GET) on ManageEngine ServiceDesk Plus Cloud entities.
  - Supports Requests, Problems, Changes, and Releases.
  - If C(parent_id) is provided, retrieves a single record. Otherwise, retrieves a list of records.
extends_documentation_fragment:
  - manageengine.sdp_cloud.sdp
options:
  payload:
    description:
      - The input data for the API request.
      - Used for list operations to control pagination and sorting.
      - Supported keys are C(row_count) (1-100, default 10), C(sort_field), C(sort_order) (asc/desc), C(get_total_count), and C(start_index).
      - Ignored when C(parent_id) is provided.
    type: dict
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
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.api_util import (
    SDPClient, common_argument_spec, validate_parameters, construct_endpoint,
    AUTH_MUTUALLY_EXCLUSIVE, AUTH_REQUIRED_TOGETHER
)
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.sdp_config import MODULE_CONFIG


def construct_payload(module):
    """Validate and construct the payload."""
    # ID Handling: If ID is present, no payload (list_info) is allowed/needed
    if module.params.get('parent_id'):
        return None

    payload = module.params['payload']
    if not payload:
        return None

    # Fetch configuration for validation
    parent_module = module.params['parent_module_name']
    module_config = MODULE_CONFIG.get(parent_module)

    allowed_sort_fields = module_config.get('sortable_fields', [])

    validated_payload = {}

    # Allowed keys for list_info
    allowed_keys = ['row_count', 'sort_field', 'sort_order', 'get_total_count', 'start_index']

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
    sort_field = payload.get('sort_field', 'created_time')

    # Validate against configured sortable_fields
    if allowed_sort_fields and sort_field not in allowed_sort_fields:
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
    """Main execution entry point for read module."""
    module_args = common_argument_spec()
    module_args.update(dict(
        payload=dict(type='dict')
    ))

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=AUTH_MUTUALLY_EXCLUSIVE,
        required_together=AUTH_REQUIRED_TOGETHER
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
