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

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


def test_create_complete(HeatStack, BigIP):
    hc, stack = HeatStack(os.path.join(TEST_DIR, 'success.yaml'))
    assert hc.wait_until_status(stack.id, 'create_complete') is True
    assert BigIP.tm.sys.applications.services.service.exists(
        name='test_service', partition='Common') is True


def test_create_complete_no_answers(HeatStack, BigIP):
    hc, stack = HeatStack(os.path.join(TEST_DIR, 'success_no_answers.yaml'))
    assert hc.wait_until_status(stack.id, 'create_complete') is True
    assert BigIP.tm.sys.applications.services.service.exists(
        name='test_service', partition='Common') is True
    assert BigIP.tm.sys.applications.templates.template.exists(
        name='test_template', partition='Common') is True


def test_create_complete_new_partition(HeatStack, BigIP):
    hc, stack = HeatStack(os.path.join(TEST_DIR, 'success_new_partition.yaml'))
    assert hc.wait_until_status(stack.id, 'create_complete') is True
    assert BigIP.tm.sys.applications.services.service.exists(
        name='test_service', partition='test_partition') is True
    assert BigIP.tm.sys.applications.templates.template.exists(
        name='test_template', partition='test_partition') is True
    assert BigIP.tm.sys.folders.folder.exists(name='test_partition')


# The stack deployed here depends on several pre-existing Openstack resources
# A client image is used (ubuntu), a server image with a node server
# pre-installed and networks.
def itest_create_complete_lb_deploy(HeatStackNoTeardown, BigIP):
    hc, stack = HeatStackNoTeardown(
        os.path.join(TEST_DIR, 'lb_deploy.yaml')
    )
    assert hc.wait_until_status(
        stack.id, 'create_complete', max_tries=10, interval=15
    ) is True
    assert BigIP.tm.sys.applications.services.service.exists(
        name='lb_service', partition='Common'
    ) is True
    assert BigIP.tm.sys.applications.templates.template.exists(
        name='lb_template', partition='Common'
    ) is True
    assert BigIP.tm.ltm.virtuals.virtual.exists(
        name='virtual_server1', partition='Common'
    ) is True
    assert BigIP.tm.ltm.pools.pool.exists(
        name='pool1', partition='Common'
    ) is True
    hc.delete_stack()
    assert BigIP.tm.sys.applications.services.service.exists(
        name='lb_service', partition='Common'
    ) is False
    assert BigIP.tm.sys.applications.templates.template.exists(
        name='lb_template', partition='Common'
    ) is False
    assert BigIP.tm.ltm.virtuals.virtual.exists(
        name='virtual_server1', partition='Common'
    ) is False
    assert BigIP.tm.ltm.pools.pool.exists(name='pool1', partition='Common') is \
        False
