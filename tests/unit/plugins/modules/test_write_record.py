# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import pytest
from unittest.mock import patch, MagicMock

from tests.unit.conftest import (
    FETCH_URL_PATH, build_fetch_url_response, build_fetch_url_error,
    create_mock_module,
)

from plugins.modules.write_record import (
    resolve_field_metadata, transform_field_value, construct_payload,
)
from plugins.module_utils.sdp_config import MODULE_CONFIG


# ---------------------------------------------------------------------------
# resolve_field_metadata
# ---------------------------------------------------------------------------
class TestResolveFieldMetadata:
    def test_system_field_string(self):
        module = create_mock_module({'parent_module_name': 'request'})
        config = MODULE_CONFIG['request']
        ftype, category, group = resolve_field_metadata(module, None, config, 'subject')
        assert ftype == 'string'
        assert category == 'system'
        assert group is None

    def test_system_field_lookup(self):
        module = create_mock_module({'parent_module_name': 'request'})
        config = MODULE_CONFIG['request']
        ftype, category, group = resolve_field_metadata(module, None, config, 'priority')
        assert ftype == 'lookup'
        assert category == 'system'

    def test_system_field_user(self):
        module = create_mock_module({'parent_module_name': 'request'})
        config = MODULE_CONFIG['request']
        ftype, category, group = resolve_field_metadata(module, None, config, 'requester')
        assert ftype == 'user'
        assert category == 'system'

    def test_system_field_datetime(self):
        module = create_mock_module({'parent_module_name': 'request'})
        config = MODULE_CONFIG['request']
        ftype, category, group = resolve_field_metadata(module, None, config, 'due_by_time')
        assert ftype == 'datetime'
        assert category == 'system'

    def test_grouped_field(self):
        module = create_mock_module({'parent_module_name': 'problem'})
        config = MODULE_CONFIG['problem']
        ftype, category, group = resolve_field_metadata(module, None, config, 'is_known_error')
        assert ftype == 'bool'
        assert category == 'system'
        assert group == 'known_error_details'

    def test_udf_field_without_client(self):
        module = create_mock_module({'parent_module_name': 'request'})
        config = MODULE_CONFIG['request']
        ftype, category, group = resolve_field_metadata(module, None, config, 'udf_char1')
        assert ftype == 'string'
        assert category == 'udf'
        module.warn.assert_called_once()

    def test_invalid_field(self):
        module = create_mock_module({'parent_module_name': 'request'})
        config = MODULE_CONFIG['request']
        ftype, category, group = resolve_field_metadata(module, None, config, 'nonexistent_field')
        assert ftype is None
        assert category is None
        assert group is None


# ---------------------------------------------------------------------------
# transform_field_value
# ---------------------------------------------------------------------------
class TestTransformFieldValue:
    def test_string_passthrough(self):
        module = create_mock_module({})
        assert transform_field_value(module, 'subject', 'Hello', 'string') == 'Hello'

    def test_num_passthrough(self):
        module = create_mock_module({})
        assert transform_field_value(module, 'count', 42, 'num') == 42

    def test_bool_from_string_true(self):
        module = create_mock_module({})
        assert transform_field_value(module, 'flag', 'true', 'bool') is True

    def test_bool_from_string_false(self):
        module = create_mock_module({})
        assert transform_field_value(module, 'flag', 'false', 'bool') is False

    def test_bool_from_native(self):
        module = create_mock_module({})
        assert transform_field_value(module, 'flag', True, 'bool') is True

    def test_datetime_valid(self):
        module = create_mock_module({})
        result = transform_field_value(module, 'due_by_time', 1700000000, 'datetime')
        assert result == {'value': 1700000000}

    def test_datetime_invalid(self):
        module = create_mock_module({})
        with pytest.raises(SystemExit):
            transform_field_value(module, 'due_by_time', 'not-a-timestamp', 'datetime')

    def test_lookup(self):
        module = create_mock_module({})
        result = transform_field_value(module, 'priority', 'High', 'lookup')
        assert result == {'name': 'High'}

    def test_user_by_email(self):
        module = create_mock_module({})
        result = transform_field_value(module, 'requester', 'admin@example.com', 'user')
        assert result == {'email_id': 'admin@example.com'}

    def test_user_rejects_name(self):
        """User fields accept only email_id; name (no @) should fail."""
        module = create_mock_module({})
        with pytest.raises(SystemExit):
            transform_field_value(module, 'requester', 'Administrator', 'user')
        module.fail_json.assert_called_once()
        call_msg = module.fail_json.call_args[1]['msg']
        assert 'email' in call_msg.lower()
        assert 'Administrator' in call_msg

    def test_user_rejects_invalid_email_like(self):
        """User fields reject values that have @ but no domain.tld (e.g. hell@hi)."""
        module = create_mock_module({})
        with pytest.raises(SystemExit):
            transform_field_value(module, 'requester', 'hell@hi', 'user')
        module.fail_json.assert_called_once()

    def test_user_accepts_valid_email(self):
        """User fields accept valid email (local@domain.tld)."""
        module = create_mock_module({})
        result = transform_field_value(module, 'requester', 'user@example.com', 'user')
        assert result == {'email_id': 'user@example.com'}
        result = transform_field_value(module, 'requester', 'a@b.co', 'user')
        assert result == {'email_id': 'a@b.co'}


# ---------------------------------------------------------------------------
# construct_payload
# ---------------------------------------------------------------------------
class TestConstructPayload:
    def test_none_when_no_payload(self):
        module = create_mock_module({
            'payload': None,
            'parent_module_name': 'request',
        })
        assert construct_payload(module) is None

    def test_simple_string_fields(self):
        module = create_mock_module({
            'payload': {'subject': 'Test', 'description': 'A test'},
            'parent_module_name': 'request',
        })
        result = construct_payload(module)
        assert result == {
            'request': {
                'subject': 'Test',
                'description': 'A test',
            }
        }

    def test_lookup_field_transformation(self):
        module = create_mock_module({
            'payload': {'priority': 'High'},
            'parent_module_name': 'request',
        })
        result = construct_payload(module)
        assert result['request']['priority'] == {'name': 'High'}

    def test_user_field_transformation(self):
        module = create_mock_module({
            'payload': {'requester': 'admin@example.com'},
            'parent_module_name': 'request',
        })
        result = construct_payload(module)
        assert result['request']['requester'] == {'email_id': 'admin@example.com'}

    def test_grouped_fields(self):
        module = create_mock_module({
            'payload': {'is_known_error': 'true', 'known_error_comments': 'Some comment'},
            'parent_module_name': 'problem',
        })
        result = construct_payload(module)
        assert 'known_error_details' in result['problem']
        assert result['problem']['known_error_details']['is_known_error'] is True
        assert result['problem']['known_error_details']['known_error_comments'] == 'Some comment'

    def test_invalid_field_fails(self):
        module = create_mock_module({
            'payload': {'invalid_field': 'value'},
            'parent_module_name': 'request',
        })
        with pytest.raises(SystemExit):
            construct_payload(module)
        module.fail_json.assert_called_once()

    def test_udf_field_without_client(self):
        module = create_mock_module({
            'payload': {'udf_char1': 'value'},
            'parent_module_name': 'request',
        })
        result = construct_payload(module)
        assert 'udf_fields' in result['request']
        assert result['request']['udf_fields']['udf_char1'] == 'value'

    def test_mixed_fields(self):
        module = create_mock_module({
            'payload': {
                'subject': 'Test',
                'priority': 'High',
                'requester': 'admin@example.com',
            },
            'parent_module_name': 'request',
        })
        result = construct_payload(module)
        assert result['request']['subject'] == 'Test'
        assert result['request']['priority'] == {'name': 'High'}
        assert result['request']['requester'] == {'email_id': 'admin@example.com'}
