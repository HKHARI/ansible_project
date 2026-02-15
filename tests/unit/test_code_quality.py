# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import subprocess
import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))


def test_no_unused_imports():
    """
    Run pylint to check for unused imports in the codebase.
    This test fails if any unused imports are found.
    """
    # Paths to check
    paths_to_check = [
        os.path.join(REPO_ROOT, 'plugins'),
        os.path.join(REPO_ROOT, 'tests'),
    ]

    # Command to run pylint
    # --disable=all: Disable all checks
    # --enable=unused-import: Enable only unused-import check
    # --persistent=n: Don't save stats (avoid permission issues in sandbox)
    cmd = [
        'pylint',
        '--disable=all',
        '--enable=unused-import',
        '--persistent=n',
    ] + paths_to_check

    try:
        # Run pylint
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=False
        )

        # Check output
        if result.returncode != 0:
            # Pylint returns non-zero if issues are found or if there's a fatal error
            # If output contains "unused-import", fail the test with the output
            if "unused-import" in result.stdout:
                pytest.fail(f"Unused imports found:\n{result.stdout}")
            elif result.returncode >= 32:
                 # Usage error or internal error
                 pytest.fail(f"Pylint failed to run:\n{result.stderr}\n{result.stdout}")
            # If returncode is non-zero but no unused-import in stdout, it might be other issues if enabled,
            # but here we only enabled unused-import.
            # Pylint exit codes: 1=fatal, 2=error, 4=warning, 8=refactor, 16=convention, 32=usage_error
            # unused-import is a warning (4) or convention/refactor depending on config, usually warning.

            # Double check if we actually have unused imports reported
            if "Unused import" in result.stdout or ": W0611:" in result.stdout:
                 pytest.fail(f"Unused imports found:\n{result.stdout}")

    except FileNotFoundError:
        pytest.skip("pylint not installed, skipping unused import test")
