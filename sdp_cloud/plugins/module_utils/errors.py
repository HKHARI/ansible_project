# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json


class SDPError(Exception):
    def __init__(self, message):
        super(SDPError, self).__init__(message)
        self.message = message

    def to_module_fail_json_output(self):
        return {
            "msg": str(self),
        }

    def _is_jsonable(self, x):
        try:
            json.dumps(x)
            return True
        except Exception:
            return False


class PayloadError(SDPError):
    pass


class AuthError(SDPError):
    pass


class APIError(SDPError):
    def __init__(self, status_code, message, details=None):
        self.status_code = status_code
        self.details = details
        super(APIError, self).__init__("API Error {0}: {1}".format(status_code, message))

    def to_module_fail_json_output(self):
        output = {
            "msg": self.message,
            "status_code": self.status_code,
        }
        if self.details:
            output["error_details"] = self.details
        return output


class NetworkError(SDPError):
    def __init__(self, message, original_exception=None):
        super(NetworkError, self).__init__(message)
        self.original_exception = original_exception

    def to_module_fail_json_output(self):
        output = {
            "msg": self.message,
        }
        if self.original_exception:
            output["exception"] = str(self.original_exception)
        return output
