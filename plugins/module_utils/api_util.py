# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import os
import time
from ansible.module_utils.basic import env_fallback
from ansible.module_utils.urls import fetch_url
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.oauth import get_access_token
from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.sdp_config import DC_CHOICES, MODULE_CONFIG

from ansible_collections.manageengine.sdp_cloud.plugins.module_utils.error_handler import handle_error
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


# Environment variable names for credential fallback
ENV_AUTH_TOKEN = 'SDP_CLOUD_AUTH_TOKEN'
ENV_CLIENT_ID = 'SDP_CLOUD_CLIENT_ID'
ENV_CLIENT_SECRET = 'SDP_CLOUD_CLIENT_SECRET'
ENV_REFRESH_TOKEN = 'SDP_CLOUD_REFRESH_TOKEN'


def common_argument_spec():
    """Return common argument specification for SDP modules."""
    return dict(
        domain=dict(type='str', required=True),
        portal_name=dict(type='str', required=True),
        auth_token=dict(type='str', no_log=True, fallback=(env_fallback, [ENV_AUTH_TOKEN])),
        client_id=dict(type='str', fallback=(env_fallback, [ENV_CLIENT_ID])),
        client_secret=dict(type='str', no_log=True, fallback=(env_fallback, [ENV_CLIENT_SECRET])),
        refresh_token=dict(type='str', no_log=True, fallback=(env_fallback, [ENV_REFRESH_TOKEN])),
        dc=dict(type='str', required=True, choices=DC_CHOICES),
        parent_module_name=dict(type='str', required=True, choices=list(MODULE_CONFIG.keys())),
        parent_id=dict(type='str'),
    )


def get_auth_params(module):
    """Resolve auth credentials from module params, falling back to env vars.

    Returns:
        A dict with keys: auth_token, client_id, client_secret, refresh_token.
        Fails the module if no valid credential set is found.
    """
    auth_token = module.params.get('auth_token') or os.environ.get(ENV_AUTH_TOKEN)
    client_id = module.params.get('client_id') or os.environ.get(ENV_CLIENT_ID)
    client_secret = module.params.get('client_secret') or os.environ.get(ENV_CLIENT_SECRET)
    refresh_token = module.params.get('refresh_token') or os.environ.get(ENV_REFRESH_TOKEN)

    if not auth_token and not (client_id and client_secret and refresh_token):
        module.fail_json(
            msg="Missing required credentials. Provide 'auth_token' or "
                "('client_id', 'client_secret', 'refresh_token') via module params "
                "or environment variables (SDP_CLOUD_AUTH_TOKEN, SDP_CLOUD_CLIENT_ID, "
                "SDP_CLOUD_CLIENT_SECRET, SDP_CLOUD_REFRESH_TOKEN)."
        )

    return {
        'auth_token': auth_token,
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
    }


def check_module_config(module):
    """Validate that the parent module is configured in MODULE_CONFIG."""
    parent_module = module.params['parent_module_name']

    # Hierarchy Validation
    parent_config = MODULE_CONFIG.get(parent_module)
    if not parent_config:
        module.fail_json(msg="Invalid parent_module_name: {0}".format(parent_module))

    return True


def construct_endpoint(module, operation=None):
    """Construct the API endpoint based on hierarchy."""
    parent_module = module.params['parent_module_name']
    parent_id = module.params.get('parent_id')

    # Get endpoints from config
    parent_config = MODULE_CONFIG.get(parent_module)
    endpoint = parent_config['endpoint']

    if parent_id:
        endpoint += "/{0}".format(parent_id)

    # Append convenience operation at the deepest level
    if operation:
        endpoint += "/{0}".format(operation)

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

    # HTTP status codes that are safe to retry (transient errors)
    RETRYABLE_STATUS_CODES = (429, 500, 502, 503, 504)

    def _ensure_auth(self):
        """Ensure we have a valid auth token, generating one if needed.

        Resolves credentials from module params first, then falls back to
        environment variables via get_auth_params().
        """
        if not self.auth_token:
            auth = get_auth_params(self.module)
            self.auth_token = auth['auth_token']
            self.client_id = auth['client_id']
            self.client_secret = auth['client_secret']
            self.refresh_token = auth['refresh_token']

        if not self.auth_token:
            if self.client_id and self.client_secret and self.refresh_token:
                token_data = get_access_token(
                    self.module, self.client_id, self.client_secret,
                    self.refresh_token, self.dc
                )
                self.auth_token = token_data['access_token']
            else:
                self.module.fail_json(
                    msg="Missing authentication credentials."
                )

    def request(self, endpoint, method='GET', data=None, max_retries=3, retry_delay=2):
        """Make API request with exponential backoff for transient errors.

        Args:
            endpoint: API endpoint path (appended to base_url).
            method: HTTP method (GET, POST, PUT, DELETE).
            data: Request payload dict (will be JSON-encoded).
            max_retries: Maximum number of retry attempts for transient errors.
            retry_delay: Base delay in seconds between retries (doubles each attempt).

        Returns:
            Parsed JSON response dict from the API.
        """
        self._ensure_auth()

        url = "{0}/{1}".format(self.base_url, endpoint)

        headers = {
            'Authorization': 'Zoho-oauthtoken {0}'.format(self.auth_token),
            'Accept': 'application/vnd.manageengine.sdp.v3+json'
        }
        payload = None
        if data:
            payload = urllib_parse.urlencode({'input_data': json.dumps(data)})
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

        last_info = None
        for attempt in range(max_retries + 1):
            response, info = fetch_url(
                self.module,
                url,
                data=payload,
                method=method,
                headers=headers
            )

            status_code = info.get('status', -1)
            last_info = info

            # If request succeeded (response is not None), break out of retry loop
            if response:
                break

            # Check if the error is retryable
            if status_code in self.RETRYABLE_STATUS_CODES and attempt < max_retries:
                delay = retry_delay * (2 ** attempt)
                self.module.warn(
                    "Request to {0} returned HTTP {1}, retrying in {2}s (attempt {3}/{4})".format(
                        url, status_code, delay, attempt + 1, max_retries
                    )
                )
                time.sleep(delay)
                continue

            # Non-retryable error or retries exhausted
            handle_error(self.module, info, "API Request Failed")

        return self._parse_response(response, last_info)

    def _parse_response(self, response, info):
        """Parse and validate the API response."""
        status_code = info.get('status', -1)
        body = response.read()

        # Treat HTTP 4xx/5xx as failure (e.g. 404 wrong endpoint) so we don't return changed=True
        if status_code >= 400:
            error_info = dict(info)
            if body:
                error_info['body'] = body.decode('utf-8', errors='replace') if isinstance(body, bytes) else body
            handle_error(self.module, error_info, "API Request Failed")

        if not body:
            return {"status": status_code, "msg": "Empty response body"}

        try:
            result = json.loads(body)
        except ValueError:
            self.module.fail_json(msg="Invalid JSON response from SDP API", raw_response=body)

        # Check for API-level errors even on HTTP 200
        if isinstance(result, dict):
            resp_status = result.get('response_status', {})
            if isinstance(resp_status, dict) and resp_status.get('status_code', 2000) >= 4000:
                self.module.fail_json(
                    msg="{0}".format(resp_status.get('messages', [{}])[0].get('message', 'API Error')),
                    status=resp_status.get('status_code'),
                    response=result
                )

        return result

    def get_record(self, endpoint):
        """Fetch a single record by endpoint. Returns None if not found (HTTP 404)."""
        self._ensure_auth()

        url = "{0}/{1}".format(self.base_url, endpoint)

        headers = {
            'Authorization': 'Zoho-oauthtoken {0}'.format(self.auth_token),
            'Accept': 'application/v3+json'
        }

        response, info = fetch_url(
            self.module,
            url,
            method='GET',
            headers=headers
        )

        status_code = info.get('status', -1)

        # 404 means record does not exist -- return None instead of failing
        if status_code == 404 or not response:
            return None

        body = response.read()
        if not body:
            return None

        try:
            return json.loads(body)
        except ValueError:
            return None


def get_current_record(client, module):
    """Fetch the current state of a record for idempotency checks.

    Returns:
        The record dict (e.g., response['request']) if found, or None if no parent_id
        or record does not exist.
    """
    parent_id = module.params.get('parent_id')
    if not parent_id:
        return None

    endpoint = construct_endpoint(module)
    result = client.get_record(endpoint)

    if not result:
        return None

    # The API wraps the record under the module name key (e.g., 'request', 'problem')
    parent_module = module.params['parent_module_name']
    return result.get(parent_module)


def has_differences(desired_payload, current_record, parent_module):
    """Compare the desired payload against the current record to detect changes.

    Performs a shallow comparison of the fields present in the desired payload
    against the current record. Only fields specified in the payload are compared.

    Args:
        desired_payload: The constructed API payload dict (e.g., {'request': {...}}).
        current_record: The current record dict from the API.
        parent_module: The module name key (e.g., 'request').

    Returns:
        True if there are differences, False if the desired state matches current.
    """
    if not desired_payload or not current_record:
        return True

    desired_fields = desired_payload.get(parent_module, {})

    for key, desired_value in desired_fields.items():
        current_value = current_record.get(key)

        if key == 'udf_fields':
            # Compare UDF fields individually
            current_udfs = current_record.get('udf_fields', {})
            for udf_key, udf_value in desired_value.items():
                if not _values_match(udf_value, current_udfs.get(udf_key)):
                    return True
            continue

        if not _values_match(desired_value, current_value):
            return True

    return False


def _values_match(desired, current):
    """Compare a desired value with the current value from the API.

    Handles the various SDP API value formats:
    - lookup fields: {'name': 'value'} compared to {'name': 'value', 'id': '123', ...}
    - user fields: {'email_id': 'value'} (only email_id is accepted as input)
    - datetime fields: {'value': timestamp}
    - scalar fields: direct comparison

    Returns:
        True if the values match, False otherwise.
    """
    if desired is None and current is None:
        return True
    if desired is None or current is None:
        return False

    # Both are dicts: compare the keys present in desired
    if isinstance(desired, dict) and isinstance(current, dict):
        for k, v in desired.items():
            if current.get(k) != v:
                return False
        return True

    # Direct scalar comparison
    return desired == current
