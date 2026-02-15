# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import patch

from tests.unit.conftest import (
    FETCH_URL_PATH, build_fetch_url_response, build_fetch_url_error,
    create_mock_module,
)

from plugins.module_utils.api_util import (
    SDPClient, common_argument_spec, check_module_config,
    construct_endpoint, get_current_record, has_differences, _values_match,
)


# ---------------------------------------------------------------------------
# common_argument_spec
# ---------------------------------------------------------------------------
class TestCommonArgumentSpec:
    def test_returns_expected_keys(self):
        spec = common_argument_spec()
        expected_keys = {
            'domain', 'portal_name', 'auth_token', 'client_id',
            'client_secret', 'refresh_token', 'dc', 'parent_module_name',
            'parent_id',
        }
        assert set(spec.keys()) == expected_keys

    def test_required_fields(self):
        spec = common_argument_spec()
        assert spec['domain']['required'] is True
        assert spec['portal_name']['required'] is True
        assert spec['dc']['required'] is True
        assert spec['parent_module_name']['required'] is True

    def test_no_log_fields(self):
        spec = common_argument_spec()
        assert spec['auth_token'].get('no_log') is True
        assert spec['client_secret'].get('no_log') is True
        assert spec['refresh_token'].get('no_log') is True


# ---------------------------------------------------------------------------
# check_module_config
# ---------------------------------------------------------------------------
class TestCheckModuleConfig:
    def test_valid_module(self):
        module = create_mock_module({'parent_module_name': 'request'})
        assert check_module_config(module) is True

    def test_invalid_module_name(self):
        module = create_mock_module({'parent_module_name': 'invalid_module'})
        with pytest.raises(SystemExit):
            check_module_config(module)
        module.fail_json.assert_called_once()


# ---------------------------------------------------------------------------
# construct_endpoint
# ---------------------------------------------------------------------------
class TestConstructEndpoint:
    def test_endpoint_without_id(self):
        module = create_mock_module({
            'parent_module_name': 'request',
            'parent_id': None,
        })
        assert construct_endpoint(module) == 'requests'

    def test_endpoint_with_id(self):
        module = create_mock_module({
            'parent_module_name': 'problem',
            'parent_id': '42',
        })
        assert construct_endpoint(module) == 'problems/42'

    def test_endpoint_with_operation(self):
        module = create_mock_module({
            'parent_module_name': 'change',
            'parent_id': '10',
        })
        assert construct_endpoint(module, operation='_metainfo') == 'changes/10/_metainfo'

    def test_all_module_types(self):
        for mod, expected in [('request', 'requests'), ('problem', 'problems'),
                              ('change', 'changes'), ('release', 'releases')]:
            module = create_mock_module({'parent_module_name': mod, 'parent_id': None})
            assert construct_endpoint(module) == expected


# ---------------------------------------------------------------------------
# SDPClient
# ---------------------------------------------------------------------------
class TestSDPClient:
    def _make_client(self, params):
        module = create_mock_module(params)
        return SDPClient(module), module

    def test_base_url_construction(self):
        client, _unused = self._make_client({
            'domain': 'test.example.com',
            'portal_name': 'myportal',
            'auth_token': 'tok',
            'client_id': None, 'client_secret': None,
            'refresh_token': None, 'dc': 'US',
        })
        assert client.base_url == 'https://test.example.com/app/myportal/api/v3'

    @patch(FETCH_URL_PATH)
    def test_request_get_success(self, mock_fetch):
        api_response = {'request': {'id': '1', 'subject': 'Test'}}
        mock_fetch.return_value = build_fetch_url_response(api_response)

        client, module = self._make_client({
            'domain': 'test.example.com',
            'portal_name': 'portal',
            'auth_token': 'tok',
            'client_id': None, 'client_secret': None,
            'refresh_token': None, 'dc': 'US',
        })

        result = client.request('requests/1', method='GET')
        assert result == api_response
        mock_fetch.assert_called_once()

    @patch(FETCH_URL_PATH)
    def test_request_post_encodes_payload(self, mock_fetch):
        api_response = {'request': {'id': '99', 'subject': 'New'}}
        mock_fetch.return_value = build_fetch_url_response(api_response)

        client, module = self._make_client({
            'domain': 'test.example.com',
            'portal_name': 'portal',
            'auth_token': 'tok',
            'client_id': None, 'client_secret': None,
            'refresh_token': None, 'dc': 'US',
        })

        payload = {'request': {'subject': 'New'}}
        result = client.request('requests', method='POST', data=payload)

        assert result == api_response
        call_kwargs = mock_fetch.call_args
        assert 'input_data' in call_kwargs.kwargs.get('data', '') or 'input_data' in str(call_kwargs)

    @patch(FETCH_URL_PATH)
    def test_request_api_level_error(self, mock_fetch):
        """API returns HTTP 200 but with status_code >= 4000."""
        error_response = {
            'response_status': {
                'status_code': 4001,
                'messages': [{'message': 'Field validation failed', 'status_code': 4001}]
            }
        }
        mock_fetch.return_value = build_fetch_url_response(error_response)

        client, module = self._make_client({
            'domain': 'test.example.com',
            'portal_name': 'portal',
            'auth_token': 'tok',
            'client_id': None, 'client_secret': None,
            'refresh_token': None, 'dc': 'US',
        })

        with pytest.raises(SystemExit):
            client.request('requests', method='POST', data={'request': {}})
        module.fail_json.assert_called_once()

    @patch(FETCH_URL_PATH)
    def test_request_http_error_calls_handle_error(self, mock_fetch):
        mock_fetch.return_value = build_fetch_url_error(401, msg='Unauthorized')

        client, module = self._make_client({
            'domain': 'test.example.com',
            'portal_name': 'portal',
            'auth_token': 'tok',
            'client_id': None, 'client_secret': None,
            'refresh_token': None, 'dc': 'US',
        })

        with pytest.raises(SystemExit):
            client.request('requests', method='GET', max_retries=0)
        module.fail_json.assert_called_once()

    @patch(FETCH_URL_PATH)
    def test_request_404_with_body_fails_not_changed(self, mock_fetch):
        """When server returns 404 with a body (e.g. wrong endpoint), task must fail, not return changed=True."""
        mock_fetch.return_value = build_fetch_url_response({'error': 'Not Found'}, status=404)

        client, module = self._make_client({
            'domain': 'test.example.com',
            'portal_name': 'portal',
            'auth_token': 'tok',
            'client_id': None, 'client_secret': None,
            'refresh_token': None, 'dc': 'US',
        })

        with pytest.raises(SystemExit):
            client.request('wrong_endpoint', method='POST', data={'request': {'subject': 'Test'}})
        module.fail_json.assert_called_once()
        call_kwargs = module.fail_json.call_args[1]
        assert call_kwargs.get('status') == 404
        # error_details is parsed JSON (dict), not a string
        assert isinstance(call_kwargs.get('error_details'), dict)
        assert call_kwargs['error_details'] == {'error': 'Not Found'}

    @patch(FETCH_URL_PATH)
    @patch('plugins.module_utils.api_util.time.sleep')
    def test_request_retries_on_transient_errors(self, mock_sleep, mock_fetch):
        """Retry on 503 then succeed on second attempt."""
        success_response = build_fetch_url_response({'request': {'id': '1'}})
        error_response = build_fetch_url_error(503, msg='Service Unavailable')

        mock_fetch.side_effect = [error_response, success_response]

        client, module = self._make_client({
            'domain': 'test.example.com',
            'portal_name': 'portal',
            'auth_token': 'tok',
            'client_id': None, 'client_secret': None,
            'refresh_token': None, 'dc': 'US',
        })

        result = client.request('requests/1', method='GET', max_retries=3, retry_delay=1)
        assert result == {'request': {'id': '1'}}
        assert mock_fetch.call_count == 2
        mock_sleep.assert_called_once_with(1)  # retry_delay * 2^0

    @patch(FETCH_URL_PATH)
    def test_get_record_returns_none_on_404(self, mock_fetch):
        mock_fetch.return_value = build_fetch_url_error(404, msg='Not Found')

        client, module = self._make_client({
            'domain': 'test.example.com',
            'portal_name': 'portal',
            'auth_token': 'tok',
            'client_id': None, 'client_secret': None,
            'refresh_token': None, 'dc': 'US',
        })

        result = client.get_record('requests/999')
        assert result is None

    @patch(FETCH_URL_PATH)
    def test_get_record_returns_data(self, mock_fetch):
        record = {'request': {'id': '1', 'subject': 'Test'}}
        mock_fetch.return_value = build_fetch_url_response(record)

        client, module = self._make_client({
            'domain': 'test.example.com',
            'portal_name': 'portal',
            'auth_token': 'tok',
            'client_id': None, 'client_secret': None,
            'refresh_token': None, 'dc': 'US',
        })

        result = client.get_record('requests/1')
        assert result == record

    def test_missing_auth_fails(self):
        client, module = self._make_client({
            'domain': 'test.example.com',
            'portal_name': 'portal',
            'auth_token': None,
            'client_id': None, 'client_secret': None,
            'refresh_token': None, 'dc': 'US',
        })

        with pytest.raises(SystemExit):
            client.request('requests', method='GET', max_retries=0)
        module.fail_json.assert_called_once()


# ---------------------------------------------------------------------------
# get_current_record
# ---------------------------------------------------------------------------
class TestGetCurrentRecord:
    @patch(FETCH_URL_PATH)
    def test_returns_none_without_parent_id(self, mock_fetch):
        module = create_mock_module({
            'parent_module_name': 'request',
            'parent_id': None,
            'domain': 'test.example.com',
            'portal_name': 'portal',
            'auth_token': 'tok',
            'client_id': None, 'client_secret': None,
            'refresh_token': None, 'dc': 'US',
        })
        client = SDPClient(module)
        assert get_current_record(client, module) is None

    @patch(FETCH_URL_PATH)
    def test_returns_record_when_found(self, mock_fetch):
        record_data = {'request': {'id': '1', 'subject': 'Test'}}
        mock_fetch.return_value = build_fetch_url_response(record_data)

        module = create_mock_module({
            'parent_module_name': 'request',
            'parent_id': '1',
            'domain': 'test.example.com',
            'portal_name': 'portal',
            'auth_token': 'tok',
            'client_id': None, 'client_secret': None,
            'refresh_token': None, 'dc': 'US',
        })
        client = SDPClient(module)
        result = get_current_record(client, module)
        assert result == {'id': '1', 'subject': 'Test'}

    @patch(FETCH_URL_PATH)
    def test_returns_none_on_404(self, mock_fetch):
        mock_fetch.return_value = build_fetch_url_error(404, msg='Not Found')

        module = create_mock_module({
            'parent_module_name': 'request',
            'parent_id': '999',
            'domain': 'test.example.com',
            'portal_name': 'portal',
            'auth_token': 'tok',
            'client_id': None, 'client_secret': None,
            'refresh_token': None, 'dc': 'US',
        })
        client = SDPClient(module)
        result = get_current_record(client, module)
        assert result is None


# ---------------------------------------------------------------------------
# has_differences / _values_match
# ---------------------------------------------------------------------------
class TestHasDifferences:
    def test_no_differences_scalar(self):
        desired = {'request': {'subject': 'Test', 'description': 'Desc'}}
        current = {'subject': 'Test', 'description': 'Desc', 'id': '1'}
        assert has_differences(desired, current, 'request') is False

    def test_has_differences_scalar(self):
        desired = {'request': {'subject': 'Updated'}}
        current = {'subject': 'Original', 'id': '1'}
        assert has_differences(desired, current, 'request') is True

    def test_no_differences_lookup(self):
        desired = {'request': {'priority': {'name': 'High'}}}
        current = {'priority': {'name': 'High', 'id': '3'}, 'id': '1'}
        assert has_differences(desired, current, 'request') is False

    def test_has_differences_lookup(self):
        desired = {'request': {'priority': {'name': 'Low'}}}
        current = {'priority': {'name': 'High', 'id': '3'}, 'id': '1'}
        assert has_differences(desired, current, 'request') is True

    def test_no_differences_udf(self):
        desired = {'request': {'udf_fields': {'udf_char1': 'value'}}}
        current = {'udf_fields': {'udf_char1': 'value', 'udf_char2': 'other'}, 'id': '1'}
        assert has_differences(desired, current, 'request') is False

    def test_has_differences_udf(self):
        desired = {'request': {'udf_fields': {'udf_char1': 'new_value'}}}
        current = {'udf_fields': {'udf_char1': 'old_value'}, 'id': '1'}
        assert has_differences(desired, current, 'request') is True

    def test_none_desired_returns_true(self):
        assert has_differences(None, {'id': '1'}, 'request') is True

    def test_none_current_returns_true(self):
        assert has_differences({'request': {'subject': 'Test'}}, None, 'request') is True


class TestValuesMatch:
    def test_both_none(self):
        assert _values_match(None, None) is True

    def test_one_none(self):
        assert _values_match('value', None) is False
        assert _values_match(None, 'value') is False

    def test_scalar_match(self):
        assert _values_match('hello', 'hello') is True
        assert _values_match(42, 42) is True

    def test_scalar_mismatch(self):
        assert _values_match('hello', 'world') is False

    def test_dict_subset_match(self):
        desired = {'name': 'High'}
        current = {'name': 'High', 'id': '3', 'color': 'red'}
        assert _values_match(desired, current) is True

    def test_dict_subset_mismatch(self):
        desired = {'name': 'Low'}
        current = {'name': 'High', 'id': '3'}
        assert _values_match(desired, current) is False

    def test_dict_vs_scalar(self):
        assert _values_match({'name': 'x'}, 'x') is False
