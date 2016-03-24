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

import plugin_test_utils as utils

import pytest

PLUGIN = 'f5_ltm_virtualserver'


def test_create_complete(HeatStack, BigIP):
    test_template = utils.get_template_file(PLUGIN, 'success.yaml')
    hc, stack = HeatStack(test_template)
    assert utils.wait_until_status(hc, stack.id, 'create_complete') is True
    assert BigIP.ltm.virtuals.virtual.exists(
        name='test_vs', partition='Common'
    ) is True


def test_create_complete_new_partition(HeatStack, BigIP):
    new_part_template = utils.get_template_file(PLUGIN, 'new_partition.yaml')
    hc, stack = HeatStack(new_part_template)
    assert utils.wait_until_status(hc, stack.id, 'create_complete') is True
    assert BigIP.ltm.virtuals.virtual.exists(
        name='test_vs', partition='test_partition'
    ) is True
    assert BigIP.sys.folders.folder.exists(name='test_partition') is True
