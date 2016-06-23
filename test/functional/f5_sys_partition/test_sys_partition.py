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
from pytest import symbols

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


def test_create_complete(HeatStack):
    HeatStack(
        os.path.join(TEST_DIR, 'success.yaml'),
        'success_test',
        parameters={
            'bigip_ip': symbols.bigip_ip,
            'bigip_un': symbols.bigip_un,
            'bigip_pw': symbols.bigip_pw
        }
    )


def test_create_complete_new_partition(HeatStack, bigip):
    hc, stack = HeatStack(
        os.path.join(TEST_DIR, 'new_partition.yaml'),
        'new_partition_test',
        parameters={
            'bigip_ip': symbols.bigip_ip,
            'bigip_un': symbols.bigip_un,
            'bigip_pw': symbols.bigip_pw
        },
        teardown=False
    )
    assert bigip.tm.sys.folders.folder.exists(name='test_partition') is True
    hc.delete_stack(stack.id)
    assert bigip.tm.sys.folders.folder.exists(name='test_partition') is False


def test_create_failed_bad_subpath(HeatStack, bigip):
    msg = '(/BadSubPath) folder does not exist'
    hc, stack = HeatStack(
        os.path.join(TEST_DIR, 'bad_subpath.yaml'),
        'bad_subpath_test',
        parameters={
            'bigip_ip': symbols.bigip_ip,
            'bigip_un': symbols.bigip_un,
            'bigip_pw': symbols.bigip_pw
        },
        expect_fail=True
    )
    assert msg in stack.stack_status_reason
    assert bigip.tm.sys.folders.folder.exists(name='test_partition') is False
