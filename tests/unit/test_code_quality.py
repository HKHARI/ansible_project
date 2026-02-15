# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import subprocess
import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

PATHS_TO_CHECK = [
    os.path.join(REPO_ROOT, 'plugins'),
    os.path.join(REPO_ROOT, 'tests'),
]


def test_no_unused_imports():
    """Run pylint to check for unused imports in the codebase."""
    cmd = [
        'pylint',
        '--disable=all',
        '--enable=unused-import',
        '--persistent=n',
    ] + PATHS_TO_CHECK

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=False,
        )

        if result.returncode != 0:
            if "unused-import" in result.stdout:
                pytest.fail("Unused imports found:\n{0}".format(result.stdout))
            if result.returncode >= 32:
                pytest.fail("Pylint failed to run:\n{0}\n{1}".format(result.stderr, result.stdout))
            if "Unused import" in result.stdout or ": W0611:" in result.stdout:
                pytest.fail("Unused imports found:\n{0}".format(result.stdout))

    except FileNotFoundError:
        pytest.skip("pylint not installed, skipping unused import test")


def test_pep8_compliance():
    """Run pycodestyle (pep8) to catch style issues before ansible-sanity does.

    E402 is excluded because Ansible modules require DOCUMENTATION/EXAMPLES/RETURN
    strings before imports -- this is standard practice and ansible-sanity allows it.
    """
    cmd = [
        'pycodestyle',
        '--max-line-length=160',
        '--ignore=E402',
        '--statistics',
    ] + PATHS_TO_CHECK

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=False,
        )

        if result.returncode != 0:
            pytest.fail("PEP8 violations found:\n{0}".format(result.stdout))

    except FileNotFoundError:
        pytest.skip("pycodestyle not installed, skipping pep8 test")
