# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.api_util import (
    SDPClient, common_argument_spec, validate_parameters, construct_endpoint,
    AUTH_MUTUALLY_EXCLUSIVE, AUTH_REQUIRED_TOGETHER
)
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.errors import SDPError


def construct_payload(module):
    """Validate and construct the payload."""
    payload = module.params['payload']
    if not payload:
        return None

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
    # Removed strict validation against module specific fields
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


def run_read_module(module_name=None, child_module_name=None):
    """Main execution entry point for read modules."""
    module_args = common_argument_spec(with_payload=True)

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False,
        mutually_exclusive=AUTH_MUTUALLY_EXCLUSIVE,
        required_together=AUTH_REQUIRED_TOGETHER
    )

    if module_name:
        module.params['parent_module_name'] = module_name

    if child_module_name:
        module.params['child_module_name'] = child_module_name

    try:
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
    except SDPError as e:
        module.fail_json(**e.to_module_fail_json_output())
