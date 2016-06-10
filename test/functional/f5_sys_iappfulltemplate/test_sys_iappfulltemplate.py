# Copyright 2015-2016 F5 Networks Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import functional.plugin_test_utils as utils

import os
import pytest

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


def test_create_complete(HeatStack, BigIP):
    hc, stack = HeatStack(
        os.path.join(TEST_DIR, 'success_common_partition.yaml')
    )
    assert hc.wait_until_status(stack.id, 'create_complete') is True
    assert BigIP.tm.sys.applications.templates.template.exists(
        name='thanks_world', partition='Common') is True


def test_create_complete_new_partition(HeatStack, BigIP):
    hc, stack = HeatStack(
        os.path.join(TEST_DIR, 'success_new_partition.yaml')
    )
    assert hc.wait_until_status(stack.id, 'create_complete') is True
    assert BigIP.tm.sys.applications.templates.template.exists(
        name='thanks_world', partition='test_partition') is True


def itest_create_failed_literal_partition(HeatStack, BigIP):
    literal_partition_template = utils.get_template_file(
        os.path.join(TEST_DIR, 'literal_partition.yaml')
    )
    msg = ''
    hc, stack = utils.ensure_failed_stack(
        HeatStack, literal_partition_template, msg
    )
    # Heat teardown fails now due to bug: Issue #23 in github


def test_create_failed_bad_iapp_parsing(HeatStackNoTeardown, BigIP):
    with pytest.raises(Exception) as ex:
        HeatStackNoTeardown(os.path.join(TEST_DIR, 'bad_iapp.yaml'))
    assert BigIP.tm.sys.applications.templates.template.exists(
        name='thanks_world', partition='Common') is False
    assert 'NonextantSectionException' in ex.value.message
