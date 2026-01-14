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
        'endpoint': 'requests',
        'supported_payload_fields': [
            'subject', 'description', 'short_description', 'requester', 'technician', 'group',
            'priority', 'template', 'status', 'site', 'request_type', 'email_ids_to_notify',
            'mode', 'attachments', 'resolution', 'closure_comments', 'closure_code', 'assets',
            'service_category', 'urgent', 'impact', 'category', 'subcategory', 'item', 'level'
        ],
        'children': {
            'note': {
                'endpoint': 'notes',
                'supported_payload_fields': [
                    'description', 'mark_first_response', 'add_to_linked_requests',
                    'notify_technician', 'show_to_requester'
                ],
                'children': {}
            },
            'worklog': {
                'endpoint': 'worklogs',
                'supported_payload_fields': [
                    'description', 'owner', 'start_time', 'end_time', 'time_spent',
                    'include_nonoperational_hours', 'type', 'owner_cost', 'other_cost',
                    'total_cost', 'add_time_for_linked_requests'
                ],
                'children': {}
            },
            'task': {
                'endpoint': 'tasks',
                'supported_payload_fields': [
                    'title', 'description', 'template', 'status', 'owner', 'scheduled_start_time',
                    'scheduled_end_time', 'actual_start_time', 'actual_end_time', 'estimated_effort',
                    'percentage_completion', 'priority', 'attachments', 'group'
                ],
                'children': {}
            }
        }
    },
    'problem': {
        'endpoint': 'problems',
        'supported_payload_fields': [
            'subject', 'description', 'template', 'reported_by', 'category', 'subcategory', 'item',
            'impact', 'urgency', 'priority', 'group', 'technician', 'status', 'site', 'due_by_time',
            'assets_affected', 'close_comments'
        ],
        'children': {
            'note': {
                'endpoint': 'notes',
                'supported_payload_fields': [
                    'description', 'notify_to'
                ],
                'children': {}
            },
            'worklog': {
                'endpoint': 'worklogs',
                'children': {}
            },
            'task': {
                'endpoint': 'tasks',
                'supported_payload_fields': [
                    'title', 'description', 'template', 'status', 'owner', 'scheduled_start_time',
                    'scheduled_end_time', 'actual_start_time', 'actual_end_time', 'estimated_effort',
                    'percentage_completion', 'priority', 'attachments', 'group'
                ],
                'children': {}
            }
        }
    },
    'change': {
        'endpoint': 'changes',
        'supported_payload_fields': [
            'title', 'description', 'template', 'category', 'services', 'change_type', 'change_manager',
            'priority', 'scheduled_end_time', 'scheduled_start_time', 'impact', 'urgency', 'risk',
            'assets', 'change_requester', 'workflow', 'reason_for_change', 'roles', 'stage', 'status',
            'next_review_on'
        ],
        'children': {
            'note': {
                'endpoint': 'notes',
                'supported_payload_fields': [
                    'description', 'notify_to'
                ],
                'children': {}
            },
            'worklog': {
                'endpoint': 'worklogs',
                'children': {}
            },
            'task': {
                'endpoint': 'tasks',
                'supported_payload_fields': [
                    'title', 'description', 'template', 'status', 'owner', 'scheduled_start_time',
                    'scheduled_end_time', 'actual_start_time', 'actual_end_time', 'estimated_effort',
                    'percentage_completion', 'priority', 'attachments', 'group'
                ],
                'children': {}
            }
        }
    },
    'release': {
        'endpoint': 'releases',
        'supported_payload_fields': [
            'title', 'description', 'short_description', 'impact', 'stage', 'status', 'urgency',
            'priority', 'template', 'services', 'site', 'category', 'comment', 'next_review_on',
            'scheduled_end_time', 'scheduled_start_time', 'risk', 'group', 'release_type',
            'subcategory', 'item', 'roles', 'asset_objects'
        ],
        'children': {
            'note': {
                'endpoint': 'notes',
                'supported_payload_fields': [
                    'description', 'notify_to'
                ],
                'children': {}
            },
            'worklog': {
                'endpoint': 'worklogs',
                'children': {}
            },
            'task': {
                'endpoint': 'tasks',
                'supported_payload_fields': [
                    'title', 'description', 'template', 'status', 'owner', 'scheduled_start_time',
                    'scheduled_end_time', 'actual_start_time', 'actual_end_time', 'estimated_effort',
                    'percentage_completion', 'priority', 'attachments', 'group'
                ],
                'children': {}
            }
        }
    }
}
