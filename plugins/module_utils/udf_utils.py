# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


# Allowed UDF Prefixes (must be lowercase)
UDF_PREFIXES = ["udf_char", "udf_bool", "udf_long", "udf_double", "txt_", "num_", "date_", "dt_", "bool_", "dbl_"]

# Cache for UDF metadata to avoid repeated calls within the same execution context
# Key: module_name (e.g., 'request'), Value: { field_name: field_details }
UDF_METADATA_CACHE = {}


def is_udf_field(field_name):
    """
    Checks if a field name matches the allowed UDF prefixes.
    Case-insensitive check, but typically UDFs should be lowercase.
    """
    field_lower = field_name.lower()
    return any(field_lower.startswith(prefix) for prefix in UDF_PREFIXES)


def fetch_udf_metadata(module, client, module_name):
    """
    Fetches the metadata for the given module to retrieve UDF definitions.
    Uses SDPClient for auth handling and caching to prevent redundant API calls.
    """
    global UDF_METADATA_CACHE
    
    if module_name in UDF_METADATA_CACHE:
        return UDF_METADATA_CACHE[module_name]

    # Use construct_endpoint with '_metainfo' operation
    from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.api_util import construct_endpoint
    endpoint = construct_endpoint(module, operation='_metainfo')
    
    # SDPClient handles auth token generation/reuse and base URL
    response = client.request(endpoint, method='GET')
    
    # Parse response to get UDF fields
    # Structure: response['metainfo']['fields']['udf_fields']['fields']
    try:
        udf_definitions = response.get('metainfo', {}).get('fields', {}).get('udf_fields', {}).get('fields', {})
        UDF_METADATA_CACHE[module_name] = udf_definitions
        return udf_definitions
    except Exception as e:
        module.warn("Failed to parse UDF metadata for module {0}: {1}".format(module_name, str(e)))
        return {}


def resolve_udf_type(udf_definition):
    """
    Resolves the field type from the SDP UDF definition.
    """
    api_type = udf_definition.get('type')
    
    if api_type == 'lookup':
        # Check lookup_entity as per user requirement
        entity = udf_definition.get('lookup_entity')
        if entity in ['user', 'technician']:
            return 'user'
        
        # It's a standard lookup
        return 'lookup'

    if api_type == 'boolean':
        return 'bool'
    elif api_type == 'integer' or api_type == 'decimal' or api_type == 'double':
        return 'num'
    elif api_type == 'date' or api_type == 'datetime':
        return 'datetime'
    
    return 'string'


def get_udf_field_type(module, client, module_name, field_name):
    """
    Retrieves the type of a specific UDF field.
    Fetches and caches metadata if not already present.
    """
    # 1. Fetch/Get Metadata
    udf_defs = fetch_udf_metadata(module, client, module_name)
    
    # 2. Lookup Field
    field_key = field_name.lower()
    field_def = udf_defs.get(field_key)
    
    if not field_def:
        # Strict validation: Fail if UDF matches prefix but is not in metadata
        module.fail_json(msg="Invalid UDF field '{0}'. Field not found in module metadata.".format(field_name))

    # 3. Resolve Type
    return resolve_udf_type(field_def)
