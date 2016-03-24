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

PLUGIN = 'f5_ltm_pool'


def test_create_complete(HeatStack, BigIP):
    test_template = utils.get_template_file(PLUGIN, 'success.yaml')
    hc, stack = HeatStack(test_template)
    assert utils.wait_until_status(hc, stack.id, 'create_complete') is True
    assert BigIP.ltm.pools.pool.exists(
        name='test_pool', partition='Common'
    ) is True
    loaded_pool = BigIP.ltm.pools.pool.load(
        name='test_pool', partition='Common'
    )
    assert loaded_pool.members_s.members.exists(
        name='129.0.0.2:80', partition='Common'
    ) is True
    assert loaded_pool.members_s.members.exists(
        name='130.0.0.2:80', partition='Common'
    ) is True


# Test causes other tests to fail because the test_partition cannot be deleted
# This will be fixed in Issue #25 in f5-openstack-heat-plugins
def itest_create_complete_new_partition(HeatStack, BigIP):
    new_part_template = utils.get_template_file(PLUGIN, 'new_partition.yaml')
    hc, stack = HeatStack(new_part_template)
    assert utils.wait_until_status(hc, stack.id, 'create_complete') is True
    assert BigIP.ltm.pools.pool.exists(
        name='test_pool', partition='test_partition'
    ) is True


# Copying this with a new template, which has no pool members
def test_create_complete_new_partition(HeatStack, BigIP):
    new_part_template = utils.get_template_file(
        PLUGIN, 'new_partition_no_members.yaml'
    )
    hc, stack = HeatStack(new_part_template)
    assert utils.wait_until_status(hc, stack.id, 'create_complete') is True
    assert BigIP.ltm.pools.pool.exists(
        name='test_pool', partition='test_partition'
    ) is True


def test_create_failed_bad_members(HeatStackNoTeardown, BigIP):
    bad_member_template = utils.get_template_file(PLUGIN, 'bad_members.yaml')
    with pytest.raises(Exception) as ex:
        HeatStackNoTeardown(bad_member_template)
    assert 'Property member_port not assigned' in ex.value.message
    assert BigIP.ltm.pools.pool.exists(
        name='test_pool', partition='Common'
    ) is False