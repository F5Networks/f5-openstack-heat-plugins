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


def test_create_complete(HeatStack, mgmt_root):
    HeatStack(
        os.path.join(TEST_DIR, 'success.yaml'),
        'success_test',
        parameters={
            'bigip_ip': symbols.bigip_ip,
            'bigip_un': symbols.bigip_un,
            'bigip_pw': symbols.bigip_pw
        }
    )
    assert mgmt_root.tm.sys.application.services.service.exists(
        name='test_service', partition='Common') is True


def test_create_complete_no_answers(HeatStack, mgmt_root):
    HeatStack(
        os.path.join(TEST_DIR, 'success_no_answers.yaml'),
        'success_no_answers_test',
        parameters={
            'bigip_ip': symbols.bigip_ip,
            'bigip_un': symbols.bigip_un,
            'bigip_pw': symbols.bigip_pw
        }
    )
    assert mgmt_root.tm.sys.application.services.service.exists(
        name='test_service', partition='Common') is True
    assert mgmt_root.tm.sys.application.templates.template.exists(
        name='test_template', partition='Common') is True


def test_create_complete_new_partition(HeatStack, mgmt_root):
    HeatStack(
        os.path.join(TEST_DIR, 'success_new_partition.yaml'),
        'success_new_partition_test',
        parameters={
            'bigip_ip': symbols.bigip_ip,
            'bigip_un': symbols.bigip_un,
            'bigip_pw': symbols.bigip_pw
        }
    )
    assert mgmt_root.tm.sys.application.services.service.exists(
        name='test_service', partition='test_partition') is True
    assert mgmt_root.tm.sys.application.templates.template.exists(
        name='test_template', partition='test_partition') is True
    assert mgmt_root.tm.sys.folders.folder.exists(name='test_partition')


# The stack deployed here depends on several pre-existing Openstack resources
# A client image is used (ubuntu), a server image with a node server
# pre-installed and networks.
def itest_create_complete_lb_deploy(HeatStack, mgmt_root):
    hc, stack = HeatStack(
        os.path.join(TEST_DIR, 'lb_deploy.yaml'),
        'lb_deploy_test',
        parameters={
            'bigip_ip': symbols.bigip_ip,
            'bigip_un': symbols.bigip_un,
            'bigip_pw': symbols.bigip_pw
        },
        teardown=False
    )
    assert mgmt_root.tm.sys.application.services.service.exists(
        name='lb_service', partition='Common'
    ) is True
    assert mgmt_root.tm.sys.application.templates.template.exists(
        name='lb_template', partition='Common'
    ) is True
    assert mgmt_root.tm.ltm.virtuals.virtual.exists(
        name='virtual_server1', partition='Common'
    ) is True
    assert mgmt_root.tm.ltm.pools.pool.exists(
        name='pool1', partition='Common'
    ) is True
    hc.delete_stack()
    assert mgmt_root.tm.sys.application.services.service.exists(
        name='lb_service', partition='Common'
    ) is False
    assert mgmt_root.tm.sys.application.templates.template.exists(
        name='lb_template', partition='Common'
    ) is False
    assert mgmt_root.tm.ltm.virtuals.virtual.exists(
        name='virtual_server1', partition='Common'
    ) is False
    assert mgmt_root.tm.ltm.pools.pool.exists(name='pool1', partition='Common') is \
        False
