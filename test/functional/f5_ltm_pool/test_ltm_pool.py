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

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


def test_create_complete(HeatStack, BigIP):
    hc, stack = HeatStack(os.path.join(TEST_DIR, 'success.yaml'))
    assert hc.wait_until_status(stack.id, 'create_complete') is True
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
    hc, stack = HeatStack(os.path.join(TEST_DIR, 'new_partition.yaml'))
    assert hc.wait_until_status(stack.id, 'create_complete') is True
    assert BigIP.ltm.pools.pool.exists(
        name='test_pool', partition='test_partition'
    ) is True


# Copying this with a new template, which has no pool members
def test_create_complete_new_partition(HeatStack, BigIP):
    hc, stack = HeatStack(
        os.path.join(TEST_DIR, 'new_partition_no_members.yaml')
    )
    assert hc.wait_until_status(stack.id, 'create_complete') is True
    assert BigIP.ltm.pools.pool.exists(
        name='test_pool', partition='test_partition'
    ) is True


def test_create_failed_bad_members(HeatStackNoTeardown, BigIP):
    with pytest.raises(Exception) as ex:
        HeatStackNoTeardown(os.path.join(TEST_DIR, 'bad_members.yaml'))
    assert 'Property member_port not assigned' in ex.value.message
    assert BigIP.ltm.pools.pool.exists(
        name='test_pool', partition='Common'
    ) is False
