# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

# Configuration for 'requests' module

ALLOWED_SORT_FIELDS = [
    "created_date",
    "due_by_time",
    "subject",
    "priority",
    "status"
]

ALLOWED_PAYLOAD_FIELDS = [
    "subject",
    "description",
    "requester",
    "technician",
    "status",
    "priority",
    "level",
    "mode",
    "service_category",
    "category",
    "subcategory",
    "item",
    "group",
    "department",
    "site",
    "resolution",
    "email_ids_to_notify",
    "udf_fields",
    "assets",
    "is_escalated",
    "reported_time"
]

# Field Types Configuration
# Types: string, number, boolean, datetime, lookup, user, group, array
FIELD_TYPE_CONFIG = {
    "subject": {"type": "string"},
    "description": {"type": "string"},
    "requester": {"type": "user"},
    "technician": {"type": "user"},
    "status": {"type": "lookup"},
    "priority": {"type": "lookup"},
    "level": {"type": "lookup"},
    "mode": {"type": "lookup"},
    "service_category": {"type": "lookup"},
    "category": {"type": "lookup"},
    "subcategory": {"type": "lookup"},
    "item": {"type": "lookup"},
    "group": {"type": "lookup"},
    "department": {"type": "lookup"},
    "site": {"type": "lookup"},
    "resolution": {"type": "string"},
    "email_ids_to_notify": {"type": "array"},
    "udf_fields": {"type": "dict"},
    "assets": {"type": "array"},
    "is_escalated": {"type": "boolean"},
    "reported_time": {"type": "datetime"}
}
