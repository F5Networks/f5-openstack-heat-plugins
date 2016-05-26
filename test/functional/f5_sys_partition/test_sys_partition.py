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

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


def test_create_complete(HeatStack):
    hc, stack = HeatStack(os.path.join(TEST_DIR, 'success.yaml'))
    assert hc.wait_until_status(stack.id, 'create_complete') is True


def test_create_complete_new_partition(HeatStackNoTeardown, BigIP):
    hc, stack = HeatStackNoTeardown(
        os.path.join(TEST_DIR, 'new_partition.yaml')
    )
    assert hc.wait_until_status(stack.id, 'create_complete') is True
    assert BigIP.tm.sys.folders.folder.exists(name='test_partition') is True
    hc.delete_stack()
    assert BigIP.tm.sys.folders.folder.exists(name='test_partition') is False


def test_create_failed_bad_subpath(HeatStack, BigIP):
    msg = '(/BadSubPath) folder does not exist'
    utils.ensure_failed_stack(
        HeatStack, os.path.join(TEST_DIR, 'bad_subpath.yaml'), msg
    )
    assert BigIP.tm.sys.folders.folder.exists(name='test_partition') is False
