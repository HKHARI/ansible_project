# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import pytest

from unittest.mock import MagicMock, patch

# Paths to fetch_url -- patch both import aliases since Python may resolve to either one
# depending on import order (direct vs symlinked ansible_collections path).
FETCH_URL_PATHS = [
    'plugins.module_utils.api_util.fetch_url',
    'ansible_collections.manageengine.sdp_cloud.plugins.module_utils.api_util.fetch_url',
]

# For convenience in tests that only need one patch path
FETCH_URL_PATH = 'plugins.module_utils.api_util.fetch_url'


class FakeHTTPResponse:
    """Simulates an HTTP response object returned by fetch_url."""

    def __init__(self, body, status=200):
        self._body = body if isinstance(body, bytes) else json.dumps(body).encode('utf-8')
        self.status = status

    def read(self):
        return self._body


def build_fetch_url_response(body, status=200):
    """Build a (response, info) tuple matching fetch_url's return format."""
    response = FakeHTTPResponse(body, status)
    info = {'status': status, 'msg': 'OK', 'body': ''}
    return response, info


def build_fetch_url_error(status, msg='Error', body=None):
    """Build a (None, info) tuple for HTTP error responses."""
    info = {
        'status': status,
        'msg': msg,
        'body': json.dumps(body) if body else '',
    }
    return None, info


def create_mock_module(params, check_mode=False, diff=False):
    """Create a mock AnsibleModule with the given params."""
    module = MagicMock()
    module.params = params
    module.check_mode = check_mode
    module._diff = diff
    module.fail_json = MagicMock(side_effect=SystemExit(1))
    module.exit_json = MagicMock(side_effect=SystemExit(0))
    module.warn = MagicMock()
    return module


@pytest.fixture
def mock_module():
    """Fixture that returns a factory for creating mock modules."""
    return create_mock_module


@pytest.fixture
def base_params():
    """Common base parameters used across tests."""
    return {
        'domain': 'sdpondemand.manageengine.com',
        'portal_name': 'ithelpdesk',
        'auth_token': 'test-token-12345',
        'client_id': None,
        'client_secret': None,
        'refresh_token': None,
        'dc': 'US',
        'parent_module_name': 'request',
        'parent_id': None,
    }
