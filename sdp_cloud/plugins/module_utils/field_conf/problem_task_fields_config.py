# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

# Configuration for 'problems_tasks' module

ALLOWED_SORT_FIELDS = [
    "created_time",
    "scheduled_start_time",
    "title",
    "priority",
    "status"
]

ALLOWED_PAYLOAD_FIELDS = [
    "title",
    "description",
    "status",
    "priority",
    "owner",
    "percentage_completion",
    "scheduled_start_time",
    "scheduled_end_time",
    "actual_start_time",
    "actual_end_time",
    "additional_cost",
    "estimated_effort",
    "group",
    "udf_fields"
]

# Field Types Configuration
FIELD_TYPE_CONFIG = {
    "title": {"type": "string"},
    "description": {"type": "string"},
    "status": {"type": "lookup"},
    "priority": {"type": "lookup"},
    "owner": {"type": "user"},
    "percentage_completion": {"type": "string"},
    "scheduled_start_time": {"type": "datetime"},
    "scheduled_end_time": {"type": "datetime"},
    "actual_start_time": {"type": "datetime"},
    "actual_end_time": {"type": "datetime"},
    "additional_cost": {"type": "string"},
    "estimated_effort": {"type": "string"},
    "group": {"type": "lookup"},
    "udf_fields": {"type": "dict"}
}
