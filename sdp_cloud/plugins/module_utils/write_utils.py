# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.api_util import SDPClient, common_argument_spec, validate_parameters, construct_endpoint, fetch_udf_metadata

# Global Variables
PARENT_MODULE = None
CHILD_MODULE = None
UDF_CONFIG = None

def get_write_argument_spec():
    """Returns the argument spec for write modules."""
    module_args = common_argument_spec()
    module_args.update(dict(
        operation=dict(type='str', default='Add', choices=['Add', 'Update', 'Delete']),
        payload=dict(type='dict')
    ))
    return module_args

def load_field_config(module, module_name, child_module=None):
    """Dynamically load field configuration for the given module."""
    if child_module:
        config_name = "{0}_{1}_fields_config".format(module_name, child_module)
    else:
        config_name = "{0}_fields_config".format(module_name)
        
    config_module_name = "ansible_collections.manageengine.sdp_cloud.plugins.module_utils.field_conf.{0}".format(config_name)
    try:
        # Use __import__ for dynamic loading compatible with Ansible's module loader
        mod = __import__(config_module_name, fromlist=['ALLOWED_PAYLOAD_FIELDS', 'FIELD_TYPE_CONFIG'])
        module.debug("Successfully loaded config for {0}".format(config_name))
        return mod.ALLOWED_PAYLOAD_FIELDS, mod.FIELD_TYPE_CONFIG
    except ImportError as e:
        module.fail_json(msg="Unsupported module '{0}' or missing configuration file. Error: {1}".format(config_name, str(e)))
        return None, None # Unreachable


def _init_udf_config(module):
    """Initialize UDF configuration."""
    global UDF_CONFIG
    
    if CHILD_MODULE:
         module.fail_json(msg="UDF fields are not supported for child/grandchild modules.")
         
    if UDF_CONFIG is None:
        client = SDPClient(module)
        UDF_CONFIG = fetch_udf_metadata(module, client.client_id, client.client_secret, client.refresh_token, client.dc, client.base_url)
        module.debug("UDF config for {0}: {1}".format(PARENT_MODULE, UDF_CONFIG))


def _get_field_config(module, key, is_udf, allowed_fields, field_types):
    """Get field configuration and type."""
    if is_udf:
        _init_udf_config(module)
        udf_name = key.lower()
        if udf_name not in UDF_CONFIG:
             module.fail_json(msg="Unknown UDF field '{0}'. Please ensure the field exists in SDP.".format(udf_name))
        
        field_config = UDF_CONFIG[udf_name]
        field_type = field_config.get('type', 'string')
        return field_config, field_type
    else:
        if key not in allowed_fields:
            module.fail_json(msg="Field '{0}' is not allowed for module '{1}'. Allowed fields: {2}".format(key, PARENT_MODULE, allowed_fields))
        
        field_config = field_types.get(key)
        field_type = field_config.get('type') if field_config else 'string'
        return field_config, field_type


def _process_field_value(module, key, value, field_type):
    """Process field value based on type."""
    if field_type == 'lookup':
        return {"name": value}
    elif field_type == 'user':
        # Simple regex for email validation
        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if re.match(email_regex, str(value)):
            return {"email_id": value}
        else:
            return {"name": value}
    elif field_type == 'boolean':
        return str(value).lower()
    elif field_type == 'datetime':
         if isinstance(value, bool):
             module.fail_json(msg="Field '{0}' of type 'datetime' cannot be a boolean.".format(key))
         
         if isinstance(value, (int, float)):
             val_str = str(int(value))
         else:
             val_str = str(value).strip()
         
         if not val_str:
              module.fail_json(msg="Field '{0}' of type 'datetime' cannot be empty.".format(key))

         if val_str.isdigit():
             return {"value": val_str}
         else:
             return {"display_value": val_str}
    
    return value


def construct_payload(module):
    """Validate and construct the payload."""
    global PARENT_MODULE, CHILD_MODULE, UDF_CONFIG
    
    payload = module.params['payload']
    if not payload:
        return None

    PARENT_MODULE = module.params['parent_module_name']
    CHILD_MODULE = module.params['child_module_name']
    
    allowed_fields, field_types = load_field_config(module, PARENT_MODULE, CHILD_MODULE)
    
    new_payload = {}
    udf_payload = {}
    # Reset UDF_CONFIG for each module run if needed, but globals persist in module utils across invocations in same process only if cached.
    # Safe to assume module execution is isolated per task usually.
    
    for key, value in payload.items():
        is_udf = key.lower().startswith('udf_')
        
        # 1. Get Config and Type
        field_config, field_type = _get_field_config(module, key, is_udf, allowed_fields, field_types)

        # 3. Strict Type Validation
        if isinstance(value, dict):
             module.fail_json(msg="Field '{0}' has invalid type 'dict'. Only String, Number, and Boolean are allowed.".format(key))

        module.debug("Processing field '{0}' with type '{1}' (UDF: {2})".format(key, field_type, is_udf))

        # 4. Process Value
        processed_value = _process_field_value(module, key, value, field_type)

        # 5. Add to Payload
        if is_udf:
            udf_payload[key.lower()] = processed_value
        else:
            # Handle Grouping
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
    
    # Add UDFs to new_payload
    if udf_payload:
        new_payload['udf_fields'] = udf_payload

    # Wrap in module singular name
    return {PARENT_MODULE: new_payload}


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
        
    # Infer operation
    # If child module is involved: present of child_id -> Update, else Add
    # If only parent module: present of parent_id -> Update, else Add
    if child_module_name:
        if module.params.get('child_id'):
            module.params['operation'] = 'Update'
        else:
            module.params['operation'] = 'Add'
    else:
        if module.params.get('parent_id'):
            module.params['operation'] = 'Update'
        else:
            module.params['operation'] = 'Add'
    
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
