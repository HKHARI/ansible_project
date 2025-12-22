# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

# Configuration for 'problems' module

ALLOWED_SORT_FIELDS = [
    "reported_time",
    "due_by_time",
    "title",
    "priority",
    "urgency",
    "impact"
]

ALLOWED_PAYLOAD_FIELDS = [
    "title",
    "description",
    "reported_time",
    "due_by_time",
    "closed_time",
    "reported_by",
    "category",
    "impact",
    "priority",
    "subcategory",
    "item",
    "urgency",
    "is_known_error"
]

# Field Types Configuration
# Types: string, number, boolean, datetime, lookup, user,
FIELD_TYPE_CONFIG = {
    "title": {"type": "string"},
    "description": {"type": "string"},
    "reported_time": {"type": "datetime"},
    "due_by_time": {"type": "datetime"},
    "closed_time": {"type": "datetime"},
    "reported_by": {"type": "user"},
    "category": {"type": "lookup"},
    "impact": {"type": "lookup"},
    "priority": {"type": "lookup"},
    "subcategory": {"type": "lookup"},
    "item": {"type": "lookup"},
    "urgency": {"type": "lookup"},
    "is_known_error": {"type": "boolean", "is_group_field": True, "group_name": "known_error_details"}
}
