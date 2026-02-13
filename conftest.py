# -*- coding: utf-8 -*-
# Root conftest.py -- sets up Python path so that
# ansible_collections.manageengine.sdp_cloud resolves to this collection.

import os
import sys

# The collection root directory
COLLECTION_ROOT = os.path.dirname(os.path.abspath(__file__))

# We need:  ansible_collections/manageengine/sdp_cloud -> COLLECTION_ROOT
# Create the namespace path by going up 3 levels (to the folder containing
# ansible_collections/) or by inserting a synthetic path.

# Build a temporary namespace: <tmpdir>/ansible_collections/manageengine/sdp_cloud
# pointing back to COLLECTION_ROOT via symlinks.
import tempfile

_ns_base = os.path.join(tempfile.gettempdir(), '_ansible_test_collections')
_ns_path = os.path.join(_ns_base, 'ansible_collections', 'manageengine', 'sdp_cloud')

if not os.path.exists(_ns_path):
    os.makedirs(os.path.dirname(_ns_path), exist_ok=True)
    # Symlink the collection root into the namespace
    try:
        os.symlink(COLLECTION_ROOT, _ns_path)
    except OSError:
        pass  # Symlink already exists or permission error

# Add the namespace base to sys.path so "import ansible_collections.manageengine.sdp_cloud" works
if _ns_base not in sys.path:
    sys.path.insert(0, _ns_base)

# Also add COLLECTION_ROOT so "from plugins.*" imports work directly in tests
if COLLECTION_ROOT not in sys.path:
    sys.path.insert(0, COLLECTION_ROOT)

# Ensure module identity: when Python imports via both paths, the module objects
# must be the same. After importing via one path, register the other as an alias.
import importlib


def _ensure_module_aliases():
    """Make sure 'plugins.*' and 'ansible_collections.manageengine.sdp_cloud.plugins.*'
    resolve to the same module objects in sys.modules."""
    # Import the module_utils via the direct path first
    prefixes = [
        ('plugins.module_utils.api_util', 'ansible_collections.manageengine.sdp_cloud.plugins.module_utils.api_util'),
        ('plugins.module_utils.error_handler', 'ansible_collections.manageengine.sdp_cloud.plugins.module_utils.error_handler'),
        ('plugins.module_utils.oauth', 'ansible_collections.manageengine.sdp_cloud.plugins.module_utils.oauth'),
        ('plugins.module_utils.sdp_config', 'ansible_collections.manageengine.sdp_cloud.plugins.module_utils.sdp_config'),
        ('plugins.module_utils.udf_utils', 'ansible_collections.manageengine.sdp_cloud.plugins.module_utils.udf_utils'),
        ('plugins.modules.write_record', 'ansible_collections.manageengine.sdp_cloud.plugins.modules.write_record'),
        ('plugins.modules.read_record', 'ansible_collections.manageengine.sdp_cloud.plugins.modules.read_record'),
        ('plugins.modules.oauth_token', 'ansible_collections.manageengine.sdp_cloud.plugins.modules.oauth_token'),
    ]
    for short, long in prefixes:
        try:
            mod = importlib.import_module(short)
            sys.modules[long] = mod
        except ImportError:
            pass


_ensure_module_aliases()
