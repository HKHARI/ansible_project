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
        'children': {
            'note': {
                'endpoint': 'notes',
                'children': {}
            },
            'worklog': {
                'endpoint': 'worklogs',
                'children': {}
            },
            'task': {
                'endpoint': 'tasks',
                'children': {}
            }
        }
    },
    'problem': {
        'endpoint': 'problems',
        'children': {
            'note': {
                'endpoint': 'notes',
                'children': {}
            },
            'worklog': {
                'endpoint': 'worklogs',
                'children': {}
            },
            'task': {
                'endpoint': 'tasks',
                'children': {}
            }
        }
    },
    'change': {
        'endpoint': 'changes',
        'children': {
            'note': {
                'endpoint': 'notes',
                'children': {}
            },
            'worklog': {
                'endpoint': 'worklogs',
                'children': {}
            },
            'task': {
                'endpoint': 'tasks',
                'children': {}
            }
        }
    }
}



