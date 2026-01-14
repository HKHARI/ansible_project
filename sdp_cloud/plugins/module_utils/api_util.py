# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
from ansible.module_utils.urls import fetch_url
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.oauth import get_access_token
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.sdp_config import DC_CHOICES, MODULE_CONFIG
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.errors import SDPError, AuthError, APIError, NetworkError, PayloadError

try:
    import urllib.parse as urllib_parse
except ImportError:
    import urllib
    urllib_parse = urllib


# Auth Constants
AUTH_MUTUALLY_EXCLUSIVE = [
    ('auth_token', 'client_id'),
    ('auth_token', 'client_secret'),
    ('auth_token', 'refresh_token')
]

AUTH_REQUIRED_TOGETHER = [
    ('client_id', 'client_secret', 'refresh_token')
]


def common_argument_spec(with_payload=False):
    """Return common argument specification for SDP modules."""
    args = dict(
        domain=dict(type='str', required=True),
        portal_name=dict(type='str', required=True),
        auth_token=dict(type='str', no_log=True),
        client_id=dict(type='str'),
        client_secret=dict(type='str', no_log=True),
        refresh_token=dict(type='str', no_log=True),
        dc=dict(type='str', required=True, choices=DC_CHOICES),
        parent_module_name=dict(type='str', required=True, choices=list(MODULE_CONFIG.keys())),
        child_module_name=dict(type='str'),
        parent_id=dict(type='str'),
        child_id=dict(type='str'),
    )

    if with_payload:
        args['payload'] = dict(type='dict')

    return args





def validate_parameters(module):
    """Validate parameter dependencies and hierarchy."""
    parent_id = module.params['parent_id']
    child_id = module.params['child_id']
    parent_module = module.params['parent_module_name']
    child_module = module.params['child_module_name']

    # 1. ID Dependency Validation
    if child_id and not parent_id:
        raise SDPError("parent_id is required when child_id is provided.")

    if child_module and not parent_id:
        raise SDPError("parent_id is required when child_module_name is provided.")

    # 2. Hierarchy Validation
    parent_config = MODULE_CONFIG.get(parent_module)
    if not parent_config:
        raise SDPError("Invalid parent_module_name: {0}".format(parent_module))

    if child_module:
        children_config = parent_config.get('children', {})
        if child_module not in children_config:
            raise SDPError("Unsupported endpoint error: Child module '{0}' is not supported for parent '{1}'. Supported children: {2}".format(
                child_module, parent_module, list(children_config.keys())))
    return True


def validate_payload_fields(module, payload, parent_module, client, child_module=None):
    """
    Validate payload fields against supported fields in configuration.
    Also handles UDF validation (allowed in parent, forbidden in child).
    Checks UDFs against metadata using the provided client.
    """
    if not payload:
        return

    # Get configuration key
    parent_config = MODULE_CONFIG.get(parent_module)
    if not parent_config:
        raise PayloadError("Invalid parent module: {0}".format(parent_module))

    supported_fields = []
    if child_module:
        child_config = parent_config.get('children', {}).get(child_module)
        if not child_config:
            raise PayloadError("Invalid child module: {0}".format(child_module))
        supported_fields = child_config.get('supported_payload_fields', [])
    else:
        supported_fields = parent_config.get('supported_payload_fields', [])

    # Separate UDFs from standard fields
    udf_fields_in_payload = []
    
    for field in payload.keys():
        if field in supported_fields:
            continue

        if field.startswith('udf_'):
            if child_module:
                raise PayloadError("UDFs are not supported for child module '{0}'. Field: {1}".format(child_module, field))
            udf_fields_in_payload.append(field)
        else:
            raise PayloadError("Unsupported payload field '{0}' for module '{1}' (child: {2}). Supported fields: {3}".format(
                field, parent_module, child_module, supported_fields))

    # Validate UDFs against metadata if present
    if udf_fields_in_payload:
        module.debug("Validating UDFs: {0}".format(udf_fields_in_payload))
        # fetch_udf_metadata is defined later in this file, so we can call it if it's in scope, 
        # but Python functions are objects. Safe to call if defined in module scope.
        # We need to ensure fetch_udf_metadata is defined or available.
        # It is defined at the end of the file.
        valid_udfs = fetch_udf_metadata(module, client)
        
        for udf in udf_fields_in_payload:
            if udf not in valid_udfs:
                 raise PayloadError("Invalid UDF field '{0}'. It does not exist in the module metadata.".format(udf))


def construct_endpoint(module):
    """Construct the API endpoint based on hierarchy."""
    parent_module = module.params['parent_module_name']
    parent_id = module.params['parent_id']
    child_module = module.params['child_module_name']
    child_id = module.params['child_id']

    # Get endpoints from config
    parent_config = MODULE_CONFIG.get(parent_module)
    endpoint = parent_config['endpoint']

    if parent_id:
        endpoint += "/{0}".format(parent_id)

        if child_module:
            child_config = parent_config['children'].get(child_module)
            endpoint += "/{0}".format(child_config['endpoint'])

            if child_id:
                endpoint += "/{0}".format(child_id)

    return endpoint


class SDPClient:
    def __init__(self, module):
        self.module = module
        self.params = module.params
        self.domain = self.params.get('domain')
        self.portal = self.params.get('portal_name')
        self.auth_token = self.params.get('auth_token')

        # OAuth params
        self.client_id = self.params.get('client_id')
        self.client_secret = self.params.get('client_secret')
        self.refresh_token = self.params.get('refresh_token')
        self.dc = self.params.get('dc')

        self.base_url = "https://{0}/app/{1}/api/v3".format(self.domain, self.portal)

    def request(self, endpoint, method='GET', data=None):
        """Make API Request"""
        if not self.auth_token:
            # If auth_token not provided, generate it
            if self.client_id and self.client_secret and self.refresh_token:
                token_data = get_access_token(self.module, self.client_id, self.client_secret, self.refresh_token, self.dc)
                self.auth_token = token_data['access_token']
            else:
                raise AuthError("Missing authentication credentials. Provide either 'auth_token' or "
                                "('client_id', 'client_secret', 'refresh_token').")

        url = "{0}/{1}".format(self.base_url, endpoint)

        headers = {
            'Authorization': 'Zoho-oauthtoken {0}'.format(self.auth_token),
            'Accept': 'application/v3+json'
        }

        payload = None
        if data:
            payload = urllib_parse.urlencode({'input_data': json.dumps(data)})
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

        try:
            response, info = fetch_url(
                self.module,
                url,
                data=payload,
                method=method,
                headers=headers
            )
        except Exception as e:
            raise NetworkError("Failed to connect to SDP Cloud API: {0}".format(str(e)), original_exception=e)

        if not response:
            error_msg, details = _get_error_details(info, "API Request Failed")
            raise APIError(info.get('status'), error_msg, details)

        body = response.read()
        if not body:
            return {"status": info.get('status'), "msg": "Empty response body", "headers": info.get('headers')}

        try:
            return json.loads(body)
        except ValueError:
            raise SDPError("Invalid JSON response from SDP API. Raw response: {0}".format(body))


def _get_error_details(info, default_msg):
    """Extract error message and details from response info."""
    error_msg = info.get('msg', default_msg)
    response_body = info.get('body')
    details = response_body

    if response_body:
        try:
            err_body = json.loads(response_body)
            # SDP Cloud V3 API Error Structure
            if 'response_status' in err_body:
                msgs = err_body['response_status'].get('messages', [])
                if msgs:
                    error_msg = "{0}: {1}".format(msgs[0].get('status_code'), msgs[0].get('message'))
            else:
                error_msg = err_body.get('error', error_msg)
        except ValueError:
            pass

    return error_msg, details


def fetch_udf_metadata(module, client):
    """
    Fetch UDF metadata from the API.
    Returns a dictionary of UDF fields and their configurations.
    """
    parent_module = module.params['parent_module_name']

    # Construct URL for _metainfo
    # URL: <domain>/app/<portal>/api/v3/<parent_module_endpoint>/_metainfo
    parent_config = MODULE_CONFIG.get(parent_module)
    endpoint_name = parent_config.get('endpoint')
    endpoint = "{0}/_metainfo".format(endpoint_name)

    module.debug("Fetching UDF metadata from: {0}".format(endpoint))

    response = client.request(endpoint, method='GET')

    if not response:
        raise SDPError("Failed to fetch metadata for module '{0}'".format(parent_module))

    try:
        # Navigate the response structure: metainfo -> fields -> udf_fields
        if 'response_status' in response and response['response_status']['status_code'] != 2000:
            raise SDPError("Metadata fetch failed: {0}".format(response))

        meta_data = response.get('metainfo', {})
        if not meta_data:
            # Fallback or check if it's directly in response (some APIs differ)
            meta_data = response

        fields = meta_data.get('fields', {})
        udf_container = fields.get('udf_fields', {})
        udf_fields_metadata = udf_container.get('fields', {})
        module.debug("Fetched {0} UDF definitions".format(len(udf_fields_metadata)))
        return udf_fields_metadata
    except Exception as e:
        raise SDPError("Error parsing UDF metadata: {0}".format(str(e)))

