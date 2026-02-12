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
