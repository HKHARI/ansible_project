# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DC_MAP = {
    'US': 'https://accounts.zoho.com',
    'EU': 'https://accounts.zoho.eu',
    'IN': 'https://accounts.zoho.in',
    'AU': 'https://accounts.zoho.com.au',
    'CN': 'https://accounts.zoho.com.cn',
    'JP': 'https://accounts.zoho.jp',
    'CA': 'https://accounts.zoho.ca',
    'SA': 'https://accounts.zoho.sa'
}

DC_CHOICES = list(DC_MAP.keys())

MODULE_CONFIG = {
    'request': {
        'endpoint': 'request',
        'sortable_fields': [
            'created_time', 'due_by_time', 'first_response_due_by_time', 'last_updated_time',
            'scheduled_start_time', 'scheduled_end_time', 'subject', 'id', 'priority', 'status'
        ],
        'supported_system_field_meta': {
            'subject': {'type': 'string'},
            'description': {'type': 'string'},
            'impact_details': {'type': 'string'},
            'update_reason': {'type': 'string'},
            'status_change_comments': {'type': 'string'},
            'status': {'type': 'lookup'},
            'template': {'type': 'lookup'},
            'priority': {'type': 'lookup'},
            'urgency': {'type': 'lookup'},
            'impact': {'type': 'lookup'},
            'mode': {'type': 'lookup'},
            'level': {'type': 'lookup'},
            'site': {'type': 'lookup'},
            'group': {'type': 'lookup'},
            'category': {'type': 'lookup'},
            'subcategory': {'type': 'lookup'},
            'item': {'type': 'lookup'},
            'requester': {'type': 'user'},
            'technician': {'type': 'user'},
            'on_behalf_of': {'type': 'user'},
            'editor': {'type': 'user'},
            'due_by_time': {'type': 'datetime'},
            'first_response_due_by_time': {'type': 'datetime'},
            'scheduled_start_time': {'type': 'datetime'},
            'scheduled_end_time': {'type': 'datetime'}
        }
    },
    'problem': {
        'endpoint': 'problems',
        'sortable_fields': [
            'reported_time', 'due_by_time', 'closed_time', 'created_time', 'id', 'title', 'priority', 'status'
        ],
        'supported_system_field_meta': {
            'title': {'type': 'string'},
            'description': {'type': 'string'},
            'impact_details': {'type': 'string'},
            'reported_time': {'type': 'datetime'},
            'due_by_time': {'type': 'datetime'},
            'closed_time': {'type': 'datetime'},
            'reported_by': {'type': 'user'},
            'technician': {'type': 'user'},
            'requester': {'type': 'user'},
            'category': {'type': 'lookup'},
            'impact': {'type': 'lookup'},
            'priority': {'type': 'lookup'},
            'subcategory': {'type': 'lookup'},
            'item': {'type': 'lookup'},
            'urgency': {'type': 'lookup'},
            'site': {'type': 'lookup'},
            'group': {'type': 'lookup'},
            'status': {'type': 'lookup'},
            'template': {'type': 'lookup'},
            'impact_details_description': {'type': 'string', 'group_name': 'impact_details'},
            'root_cause_description': {'type': 'string', 'group_name': 'root_cause'},
            'symptoms_description': {'type': 'string', 'group_name': 'symptoms'},
            'known_error_comments': {'type': 'string', 'group_name': 'known_error_details'},
            'is_known_error': {'type': 'bool', 'group_name': 'known_error_details'},
            'close_details_comments': {'type': 'string', 'group_name': 'close_details'},
            'closure_code': {'type': 'lookup', 'group_name': 'close_details'},
            'resolution_details_description': {'type': 'string', 'group_name': 'resolution_details'},
            'workaround_details_description': {'type': 'string', 'group_name': 'workaround_details'}
        }
    },
    'change': {
        'endpoint': 'changes',
        'sortable_fields': [
            'created_time', 'completed_time', 'scheduled_start_time',
            'scheduled_end_time', 'id', 'title', 'priority', 'status', 'stage'
        ],
        'supported_system_field_meta': {
            'title': {'type': 'string'},
            'description': {'type': 'string'},
            'comment': {'type': 'string'},
            'retrospective': {'type': 'bool'},
            'created_time': {'type': 'datetime'},
            'completed_time': {'type': 'datetime'},
            'scheduled_start_time': {'type': 'datetime'},
            'scheduled_end_time': {'type': 'datetime'},
            'stage': {'type': 'lookup'},
            'status': {'type': 'lookup'},
            'template': {'type': 'lookup'},
            'change_requester': {'type': 'user'},
            'change_manager': {'type': 'user'},
            'change_owner': {'type': 'user'},
            'reason_for_change': {'type': 'lookup'},
            'risk': {'type': 'lookup'},
            'impact': {'type': 'lookup'},
            'priority': {'type': 'lookup'},
            'category': {'type': 'lookup'},
            'subcategory': {'type': 'lookup'},
            'item': {'type': 'lookup'},
            'urgency': {'type': 'lookup'},
            'change_type': {'type': 'lookup'},
            'site': {'type': 'lookup'},
            'group': {'type': 'lookup'},
            'workflow': {'type': 'lookup'},

            # Grouped fields
            'roll_out_plan_description': {'type': 'string', 'group_name': 'roll_out_plan'},
            'back_out_plan_description': {'type': 'string', 'group_name': 'back_out_plan'}
        }
    },
    'release': {
        'endpoint': 'releases',
        'sortable_fields': [
            'created_time', 'completed_time', 'scheduled_start_time',
            'scheduled_end_time', 'id', 'title', 'priority', 'status', 'stage'
        ],
        'supported_system_field_meta': {
            'title': {'type': 'string'},
            'description': {'type': 'string'},
            'scheduled_start_time': {'type': 'datetime'},
            'scheduled_end_time': {'type': 'datetime'},
            'created_time': {'type': 'datetime'},
            'completed_time': {'type': 'datetime'},
            'next_review_on': {'type': 'datetime'},
            'template': {'type': 'lookup'},
            'stage': {'type': 'lookup'},
            'status': {'type': 'lookup'},
            'workflow': {'type': 'lookup'},
            'release_requester': {'type': 'user'},
            'release_engineer': {'type': 'user'},
            'release_manager': {'type': 'user'},
            'reason_for_release': {'type': 'lookup'},
            'impact': {'type': 'lookup'},
            'priority': {'type': 'lookup'},
            'category': {'type': 'lookup'},
            'subcategory': {'type': 'lookup'},
            'item': {'type': 'lookup'},
            'release_type': {'type': 'lookup'},
            'urgency': {'type': 'lookup'},
            'site': {'type': 'lookup'},
            'group': {'type': 'lookup'},
            'risk': {'type': 'lookup'},

            # Grouped fields
            'roll_out_plan_description': {'type': 'string', 'group_name': 'roll_out_plan'},
            'back_out_plan_description': {'type': 'string', 'group_name': 'back_out_plan'}
        }
    }
}
