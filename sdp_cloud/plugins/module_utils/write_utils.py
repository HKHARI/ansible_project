# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.api_util import (
    SDPClient, common_argument_spec, validate_parameters, construct_endpoint,
    AUTH_MUTUALLY_EXCLUSIVE, AUTH_REQUIRED_TOGETHER, validate_payload_fields
)
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.errors import SDPError

# Global Variables
PARENT_MODULE = None
CHILD_MODULE = None





def construct_payload(module):
    """Validate and construct the payload."""
    payload = module.params['payload']
    if not payload:
        return None

    parent_module = module.params['parent_module_name']

    # Wrap in module singular name
    return {parent_module: payload}


def run_write_module(module_name=None, child_module_name=None):
    """Main execution entry point for write modules."""
    module_args = common_argument_spec(with_payload=True)

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False,
        mutually_exclusive=AUTH_MUTUALLY_EXCLUSIVE,
        required_together=AUTH_REQUIRED_TOGETHER
    )

    # If module_name is provided (for specific wrappers), force it in params
    if module_name:
        module.params['parent_module_name'] = module_name

    if child_module_name:
        module.params['child_module_name'] = child_module_name

    # Validation
    try:
        validate_parameters(module)

        client = SDPClient(module)
        endpoint = construct_endpoint(module)

        # Automatic Operation Inference
        parent_id = module.params.get('parent_id')
        child_module = module.params.get('child_module_name')
        child_id = module.params.get('child_id')

        method = 'POST'  # Default to Create

        # If updating a parent record (parent_id present, NO child module involved)
        if parent_id and not child_module:
            method = 'PUT'
        # If updating a child record (child_module AND child_id present)
        elif child_module and child_id:
            method = 'PUT'

        # Construct Payload
        data = construct_payload(module)

        # Validate Payload Fields
        validate_payload_fields(module, data, module.params.get('parent_module_name'), client, child_module)

        response = client.request(
            endpoint=endpoint,
            method=method,
            data=data
        )

        module.exit_json(changed=True, response=response, payload=data)
    except SDPError as e:
        module.fail_json(**e.to_module_fail_json_output())
