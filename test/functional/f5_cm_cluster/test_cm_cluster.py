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

from f5.bigip import ManagementRoot
from f5.multi_device.cluster import ClusterManager

import os
from pytest import symbols as symbols_data


TEST_DIR = os.path.dirname(os.path.realpath(__file__))


def get_devices():
    a = ManagementRoot(
        symbols_data.bigip_ip, symbols_data.bigip_un, symbols_data.bigip_pw
    )
    b = ManagementRoot(
        symbols_data.bigip2_ip, symbols_data.bigip_un, symbols_data.bigip_pw
    )
    return a, b


def test_create_two_member(HeatStack):
    hc, stack = HeatStack(
        os.path.join(TEST_DIR, 'success_two_member.yaml'),
        parameters={
            'bigip_ip': symbols_data.bigip_ip,
            'bigip2_ip': symbols_data.bigip2_ip
        }
    )
    assert hc.wait_until_status(stack.id, 'create_complete') is True
    a, b = get_devices()
    cm = ClusterManager(
        devices=[a, b],
        device_group_name='my_cluster',
        device_group_partition='Common',
        device_group_type='sync-failover'
    )
    assert cm.cluster.device_group_type == 'sync-failover'
    assert cm.cluster.device_group_partition == 'Common'
    assert cm.cluster.device_group_name == 'my_cluster'
