# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json


def handle_error(module, info, default_msg):
    """
    Parses SDP Cloud API error responses and fails the module with a descriptive message.
    """
    error_msg = info.get('msg', default_msg)
    response_body = info.get('body')
    error_details = response_body

    if response_body:
        if isinstance(response_body, dict):
            err_body = response_body
            error_details = err_body
        else:
            err_body = None
        try:
            if err_body is None:
                err_body = json.loads(response_body)
                error_details = err_body
            # SDP Cloud V3 API Error Structure
            if err_body and 'response_status' in err_body:
                msgs = err_body['response_status'].get('messages', [])
                if msgs:
                    error_msg = "{0}: {1}".format(msgs[0].get('status_code'), msgs[0].get('message'))
            elif err_body:
                error_msg = err_body.get('error', error_msg)
            if err_body:
                error_details = err_body
        except (ValueError, TypeError):
            pass

    module.fail_json(msg=error_msg, status=info.get('status'), error_details=error_details)
