# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from tests.unit.conftest import create_mock_module
from plugins.modules.read_record import construct_payload


class TestReadRecordConstructPayload:
    def test_returns_none_when_id_present(self):
        module = create_mock_module({
            'parent_id': '100',
            'payload': {'row_count': 10},
            'parent_module_name': 'request',
        })
        assert construct_payload(module) is None

    def test_returns_none_when_no_payload(self):
        module = create_mock_module({
            'parent_id': None,
            'payload': None,
            'parent_module_name': 'request',
        })
        assert construct_payload(module) is None

    def test_empty_payload_returns_none(self):
        """Empty dict {} is falsy -- construct_payload returns None."""
        module = create_mock_module({
            'parent_id': None,
            'payload': {},
            'parent_module_name': 'request',
        })
        assert construct_payload(module) is None

    def test_default_values(self):
        """When only row_count is specified, other fields get defaults."""
        module = create_mock_module({
            'parent_id': None,
            'payload': {'row_count': 10},
            'parent_module_name': 'request',
        })
        result = construct_payload(module)
        assert result == {
            'list_info': {
                'row_count': 10,
                'sort_field': 'created_time',
                'sort_order': 'asc',
                'get_total_count': False,
            }
        }

    def test_custom_values(self):
        module = create_mock_module({
            'parent_id': None,
            'payload': {
                'row_count': 50,
                'sort_field': 'subject',
                'sort_order': 'desc',
                'get_total_count': True,
                'start_index': 5,
            },
            'parent_module_name': 'request',
        })
        result = construct_payload(module)
        li = result['list_info']
        assert li['row_count'] == 50
        assert li['sort_field'] == 'subject'
        assert li['sort_order'] == 'desc'
        assert li['get_total_count'] is True

    def test_invalid_key_fails(self):
        module = create_mock_module({
            'parent_id': None,
            'payload': {'invalid_key': 'value'},
            'parent_module_name': 'request',
        })
        with pytest.raises(SystemExit):
            construct_payload(module)
        module.fail_json.assert_called_once()

    def test_row_count_out_of_range(self):
        module = create_mock_module({
            'parent_id': None,
            'payload': {'row_count': 200},
            'parent_module_name': 'request',
        })
        with pytest.raises(SystemExit):
            construct_payload(module)

    def test_invalid_sort_order(self):
        module = create_mock_module({
            'parent_id': None,
            'payload': {'sort_order': 'random'},
            'parent_module_name': 'request',
        })
        with pytest.raises(SystemExit):
            construct_payload(module)

    def test_invalid_sort_field(self):
        module = create_mock_module({
            'parent_id': None,
            'payload': {'sort_field': 'nonexistent_field'},
            'parent_module_name': 'request',
        })
        with pytest.raises(SystemExit):
            construct_payload(module)

    def test_get_total_count_string_true(self):
        module = create_mock_module({
            'parent_id': None,
            'payload': {'get_total_count': 'true'},
            'parent_module_name': 'request',
        })
        result = construct_payload(module)
        assert result['list_info']['get_total_count'] is True

    def test_get_total_count_invalid_string(self):
        module = create_mock_module({
            'parent_id': None,
            'payload': {'get_total_count': 'maybe'},
            'parent_module_name': 'request',
        })
        with pytest.raises(SystemExit):
            construct_payload(module)
