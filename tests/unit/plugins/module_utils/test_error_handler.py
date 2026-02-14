# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import pytest

from tests.unit.conftest import create_mock_module
from plugins.module_utils.error_handler import handle_error


class TestHandleError:
    def test_default_message(self):
        module = create_mock_module({})
        info = {'status': 500, 'msg': 'Internal Server Error'}

        with pytest.raises(SystemExit):
            handle_error(module, info, "Fallback message")

        module.fail_json.assert_called_once()
        call_kwargs = module.fail_json.call_args[1]
        assert call_kwargs['msg'] == 'Internal Server Error'
        assert call_kwargs['status'] == 500

    def test_sdp_api_error_structure(self):
        module = create_mock_module({})
        error_body = {
            'response_status': {
                'messages': [
                    {'status_code': 4001, 'message': 'Field validation failed'}
                ]
            }
        }
        info = {
            'status': 400,
            'msg': 'Bad Request',
            'body': json.dumps(error_body),
        }

        with pytest.raises(SystemExit):
            handle_error(module, info, "Default")

        call_kwargs = module.fail_json.call_args[1]
        assert '4001' in call_kwargs['msg']
        assert 'Field validation failed' in call_kwargs['msg']
        # Valid JSON body is passed as parsed dict, not string
        assert isinstance(call_kwargs['error_details'], dict)
        assert call_kwargs['error_details'] == error_body

    def test_generic_error_key(self):
        module = create_mock_module({})
        error_body = {'error': 'Something went wrong'}
        info = {
            'status': 400,
            'msg': 'Bad Request',
            'body': json.dumps(error_body),
        }

        with pytest.raises(SystemExit):
            handle_error(module, info, "Default")

        call_kwargs = module.fail_json.call_args[1]
        assert call_kwargs['msg'] == 'Something went wrong'
        assert isinstance(call_kwargs['error_details'], dict)
        assert call_kwargs['error_details'] == error_body

    def test_invalid_json_body(self):
        module = create_mock_module({})
        info = {
            'status': 500,
            'msg': 'Server Error',
            'body': 'not json at all',
        }

        with pytest.raises(SystemExit):
            handle_error(module, info, "Default")

        call_kwargs = module.fail_json.call_args[1]
        # Falls back to info['msg'] when JSON parsing fails
        assert call_kwargs['msg'] == 'Server Error'
        # Invalid JSON body is left as string
        assert call_kwargs['error_details'] == 'not json at all'

    def test_no_body(self):
        module = create_mock_module({})
        info = {'status': 404, 'msg': 'Not Found'}

        with pytest.raises(SystemExit):
            handle_error(module, info, "Default")

        call_kwargs = module.fail_json.call_args[1]
        assert call_kwargs['msg'] == 'Not Found'
        assert call_kwargs.get('error_details') is None
