# Copyright 2016 F5 Networks Inc.
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

from f5.bigip import ManagementRoot
from f5.multi_device.cluster import ClusterManager

import os
import pytest
from pytest import symbols

from heatclient.exc import HTTPException

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def dg_test_setup(request, bigip):
    a = ManagementRoot(
        symbols.bigip_ip, symbols.bigip_un, symbols.bigip_pw
    )
    b = ManagementRoot(
        symbols.bigip2_ip, symbols.bigip_un, symbols.bigip_pw
    )

    def teardown_cluster():
        test_cm.teardown()
    test_cm = ClusterManager()
    test_cm.create(
        devices=[a, b],
        device_group_name='test_group',
        device_group_partition='Common',
        device_group_type='sync-failover'
    )
    request.addfinalizer(teardown_cluster)


def test_create_complete(HeatStack, dg_test_setup):
    HeatStack(
        os.path.join(TEST_DIR, 'success.yaml'),
        'success_test',
        parameters={
            'bigip_ip': symbols.bigip_ip,
            'bigip_un': symbols.bigip_un,
            'bigip_pw': symbols.bigip_pw,
            'dg_name': 'test_group',
            'dg_part': 'Common'
        }
    )


def test_create_complete_no_dg(HeatStack):
    hc, stack = HeatStack(
        os.path.join(TEST_DIR, 'success.yaml'),
        'bad_property',
        parameters={
            'bigip_ip': symbols.bigip_ip,
            'bigip_un': symbols.bigip_un,
            'bigip_pw': symbols.bigip_pw,
            'dg_name': 'test_group',
            'dg_part': 'Common'
        },
        expect_fail=True
    )
    assert 'Device group (test_group) not found in device group sync' in \
        stack.stack_status_reason


def test_create_complete_bad_prop(HeatStack):
    with pytest.raises(HTTPException) as ex:
        HeatStack(
            os.path.join(TEST_DIR, 'bad_property.yaml'),
            'bad_property',
            parameters={
                'bigip_ip': symbols.bigip_ip,
                'bigip_un': symbols.bigip_un,
                'bigip_pw': symbols.bigip_pw
            },
            expect_fail=True
        )
    print(ex)
    assert 'Unknown Property bad_property' in ex.value.message
