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

import os
import pytest
from pytest import symbols

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


def test_create_complete(HeatStack, bigip):
    HeatStack(
        os.path.join(TEST_DIR, 'success_common_partition.yaml'),
        'success_common_partition_test',
        parameters={
            'bigip_ip': symbols.bigip_ip,
            'bigip_un': symbols.bigip_un,
            'bigip_pw': symbols.bigip_pw
        }
    )
    assert bigip.tm.sys.application.templates.template.exists(
        name='thanks_world', partition='Common'
    ) is True


def test_create_complete_new_partition(HeatStack, bigip):
    HeatStack(
        os.path.join(TEST_DIR, 'success_new_partition.yaml'),
        'success_new_partition_test',
        parameters={
            'bigip_ip': symbols.bigip_ip,
            'bigip_un': symbols.bigip_un,
            'bigip_pw': symbols.bigip_pw
        }
    )
    assert bigip.tm.sys.application.templates.template.exists(
        name='thanks_world', partition='test_partition') is True


def itest_create_failed_literal_partition(HeatStack):
    HeatStack(
        os.path.join(TEST_DIR, 'literal_partition.yaml'),
        'literal_partition_test'
    )
    # Heat teardown fails now due to bug: Issue #23 in github


def test_create_failed_bad_iapp_parsing(HeatStack, bigip):
    with pytest.raises(Exception) as ex:
        HeatStack(
            os.path.join(TEST_DIR, 'bad_iapp.yaml'),
            'bad_iapp_test',
            parameters={
                'bigip_ip': symbols.bigip_ip,
                'bigip_un': symbols.bigip_un,
                'bigip_pw': symbols.bigip_pw
            },
            expect_fail=True
        )
    assert bigip.tm.sys.application.templates.template.exists(
        name='thanks_world', partition='Common') is False
    assert 'NonextantSectionException' in ex.value.message
