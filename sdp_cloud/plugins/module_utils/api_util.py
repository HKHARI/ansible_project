# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
from ansible.module_utils.urls import fetch_url
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.oauth import get_access_token
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.sdp_config import DC_CHOICES, MODULE_CONFIG

try:
    import urllib.parse as urllib_parse
except ImportError:
    import urllib
    urllib_parse = urllib


def common_argument_spec():
    """Return common argument specification for SDP modules."""
    return dict(
        domain=dict(type='str', required=True),
        portal_name=dict(type='str', required=True),
        auth_token=dict(type='str', no_log=True),
        client_id=dict(type='str'),
        client_secret=dict(type='str', no_log=True),
        refresh_token=dict(type='str', no_log=True),
        dc=dict(type='str', required=True, choices=DC_CHOICES),
        
        parent_module_name=dict(type='str', required=True, choices=list(MODULE_CONFIG.keys())),
        child_module_name=dict(type='str'),
        grand_child_module_name=dict(type='str'),
        
        parent_id=dict(type='str'),
        child_id=dict(type='str'),
        grand_child_id=dict(type='str'),
    )


def validate_parameters(module):
    """Validate parameter dependencies and hierarchy."""
    parent_id = module.params['parent_id']
    child_id = module.params['child_id']
    grand_child_id = module.params['grand_child_id']
    
    parent_module = module.params['parent_module_name']
    child_module = module.params['child_module_name']
    grand_child_module = module.params['grand_child_module_name']

    # 1. ID Dependency Validation
    if child_id and not parent_id:
        module.fail_json(msg="parent_id is required when child_id is provided.")
    
    if grand_child_id and not (child_id and parent_id):
        module.fail_json(msg="parent_id and child_id are required when grand_child_id is provided.")

    if child_module and not parent_id:
         module.fail_json(msg="parent_id is required when child_module_name is provided.")

    if grand_child_module and not (child_module and child_id and parent_id):
        module.fail_json(msg="parent_id, child_module_name, and child_id are required when grand_child_module_name is provided.")

    # 2. Hierarchy Validation
    parent_config = MODULE_CONFIG.get(parent_module)
    if not parent_config:
        module.fail_json(msg="Invalid parent_module_name: {0}".format(parent_module))

    if child_module:
        children_config = parent_config.get('children', {})
        if child_module not in children_config:
            module.fail_json(msg="Unsupported endpoint error: Child module '{0}' is not supported for parent '{1}'. Supported children: {2}".format(
                child_module, parent_module, list(children_config.keys())))
        
        # Validate Grandchild (if applicable)
        if grand_child_module:
            child_config = children_config.get(child_module)
            grand_children_config = child_config.get('children', {})
            if grand_child_module not in grand_children_config:
                 module.fail_json(msg="Unsupported endpoint error: Grandchild module '{0}' is not supported for child '{1}'. Supported grandchildren: {2}".format(
                    grand_child_module, child_module, list(grand_children_config.keys())))


def construct_endpoint(module):
    """Construct the API endpoint based on hierarchy."""
    parent_module = module.params['parent_module_name']
    parent_id = module.params['parent_id']
    child_module = module.params['child_module_name']
    child_id = module.params['child_id']
    grand_child_module = module.params['grand_child_module_name']
    grand_child_id = module.params['grand_child_id']

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
                
                if grand_child_module:
                    grand_child_config = child_config.get('children', {}).get(grand_child_module)
                    endpoint += "/{0}".format(grand_child_config['endpoint'])
                    
                    if grand_child_id:
                        endpoint += "/{0}".format(grand_child_id)
    
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
                self.module.fail_json(msg="Missing authentication credentials. Provide either 'auth_token' or ('client_id', 'client_secret', 'refresh_token', 'dc').")

        url = "{0}/{1}".format(self.base_url, endpoint)
        
        headers = {
            'Authorization': 'Zoho-oauthtoken {0}'.format(self.auth_token),
            'Accept': 'application/v3+json'
        }
        
        payload = None
        if data:
            payload = urllib_parse.urlencode({'input_data': json.dumps(data)})
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

        response, info = fetch_url(
            self.module,
            url,
            data=payload,
            method=method,
            headers=headers
        )

        if not response:
            _handle_error(self.module, info, "API Request Failed")

        body = response.read()
        if not body:
            return {"status": info.get('status'), "msg": "Empty response body", "headers": info.get('headers')}

        try:
            return json.loads(body)
        except ValueError:
            self.module.fail_json(msg="Invalid JSON response from SDP API", raw_response=body)


def _handle_error(module, info, default_msg):
    error_msg = info.get('msg', default_msg)
    response_body = info.get('body')
    
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
    
    module.fail_json(msg=error_msg, status=info.get('status'), error_details=response_body)


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
        module.fail_json(msg="Failed to fetch metadata for module '{0}'".format(parent_module))
        
    try:
        # Navigate the response structure: metainfo -> fields -> udf_fields
        if 'response_status' in response and response['response_status']['status_code'] != 2000:
             module.fail_json(msg="Metadata fetch failed: {0}".format(response))

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
        module.fail_json(msg="Error parsing UDF metadata: {0}".format(str(e)))
        return {}
