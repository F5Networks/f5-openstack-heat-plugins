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


PLUGIN = 'f5_sys_iappservice'


def test_create_complete(HeatStack, BigIP):
    test_templ = utils.get_template_file(PLUGIN, 'success.yaml')
    hc, stack = HeatStack(test_templ)
    assert utils.wait_until_status(hc, stack.id, 'create_complete') is True
    assert BigIP.sys.applications.services.service.exists(
        name='test_service', partition='Common') is True


def test_create_complete_no_answers(HeatStack, BigIP):
    no_answer_templ = utils.get_template_file(PLUGIN, 'success_no_answers.yaml')
    hc, stack = HeatStack(no_answer_templ)
    assert utils.wait_until_status(hc, stack.id, 'create_complete') is True
    assert BigIP.sys.applications.services.service.exists(
        name='test_service', partition='Common') is True
    assert BigIP.sys.applications.templates.template.exists(
        name='test_template', partition='Common') is True


def test_create_complete_new_partition(HeatStack, BigIP):
    new_partition_templ = utils.get_template_file(
        PLUGIN, 'success_new_partition.yaml'
    )
    hc, stack = HeatStack(new_partition_templ)
    assert utils.wait_until_status(hc, stack.id, 'create_complete') is True
    assert BigIP.sys.applications.services.service.exists(
        name='test_service', partition='test_partition') is True
    assert BigIP.sys.applications.templates.template.exists(
        name='test_template', partition='test_partition') is True
    assert BigIP.sys.folders.folder.exists(name='test_partition')


# The stack deployed here depends on several pre-existing Openstack resources
# A client image is used (ubuntu), a server image with a node server
# pre-installed and networks.
def test_create_complete_lb_deploy(HeatStackNoTeardown, BigIP):
    lb_deploy_templ = utils.get_template_file(PLUGIN, 'lb_deploy.yaml')
    hc, stack = HeatStackNoTeardown(lb_deploy_templ)
    assert utils.wait_until_status(
        hc, stack.id, 'create_complete', max_tries=10, interval=15
    ) is True
    assert BigIP.sys.applications.services.service.exists(
        name='lb_service', partition='Common'
    ) is True
    assert BigIP.sys.applications.templates.template.exists(
        name='lb_template', partition='Common'
    ) is True
    assert BigIP.ltm.virtuals.virtual.exists(
        name='virtual_server1', partition='Common'
    ) is True
    assert BigIP.ltm.pools.pool.exists(name='pool1', partition='Common') is True
    utils.delete_stack(hc, utils.TESTSTACKNAME)
    assert BigIP.sys.applications.services.service.exists(
        name='lb_service', partition='Common'
    ) is False
    assert BigIP.sys.applications.templates.template.exists(
        name='lb_template', partition='Common'
    ) is False
    assert BigIP.ltm.virtuals.virtual.exists(
        name='virtual_server1', partition='Common'
    ) is False
    assert BigIP.ltm.pools.pool.exists(name='pool1', partition='Common') is \
           False