# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.api_util import (
    SDPClient, common_argument_spec, validate_parameters, construct_endpoint
)

# Global Variables
PARENT_MODULE = None
CHILD_MODULE = None


def get_write_argument_spec():
    """Returns the argument spec for write modules."""
    module_args = common_argument_spec()
    module_args.update(dict(
        operation=dict(type='str', default='Add', choices=['Add', 'Update', 'Delete']),
        payload=dict(type='dict')
    ))
    return module_args


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
    module_args = get_write_argument_spec()

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

    # If module_name is provided (for specific wrappers), force it in params
    if module_name:
        module.params['parent_module_name'] = module_name

    if child_module_name:
        module.params['child_module_name'] = child_module_name

    # Validation
    validate_parameters(module)

    client = SDPClient(module)
    endpoint = construct_endpoint(module)

    operation = module.params['operation']
    method_map = {
        'Add': 'POST',
        'Update': 'PUT',
        'Delete': 'DELETE'
    }
    method = method_map[operation]

    # Construct Payload
    data = None
    if method in ['POST', 'PUT']:
        data = construct_payload(module)

    response = client.request(
        endpoint=endpoint,
        method=method,
        data=data
    )

    module.exit_json(changed=True, response=response, payload=data)

