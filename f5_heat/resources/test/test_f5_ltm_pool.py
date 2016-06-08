# coding=utf-8
#
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
#

from f5_heat.resources import f5_ltm_pool
from heat.common import exception
from heat.common import template_format
from heat.engine.hot.template import HOTemplate20150430
from heat.engine import rsrc_defn
from heat.engine import template

import mock
import pytest


pool_defn = '''
heat_template_version: 2015-04-30
description: Testing F5 LTM Pool plugin
resources:
  bigip_rsrc:
    type: F5::BigIP::Device
    properties:
      ip: 10.0.0.1
      username: admin
      password: admin
  partition:
    type: F5::Sys::Partition
    properties:
      name: Common
      bigip_server: bigip_rsrc
  pool:
    type: F5::LTM::Pool
    properties:
      name: testing_pool
      bigip_server: bigip_rsrc
      partition: partition
      service_down_action: Reject
      members: [{'member_ip': '128.0.0.1', 'member_port': 80},
               {'member_ip': '129.0.0.1', 'member_port': 80}]
'''

bad_pool_defn = '''
heat_template_version: 2015-04-30
description: Testing F5 LTM Pool plugin
resources:
  bigip_rsrc:
    type: F5::BigIP::Device
    properties:
      ip: 10.0.0.1
      username: admin
      password: admin
  partition:
    type: F5::Sys::Partition
    properties:
      name: Common
      bigip_server: bigip_rsrc
  pool:
    type: F5::LTM::Pool
    properties:
      name: testing_pool
      partition: partition
      bad_prop: bad_prop_name
      bigip_server: bigip_rsrc
      members: [{'member_ip': '128.0.0.1','member_port': 80},
                {'member_ip': '129.0.0.1', 'member_port': 80}]
'''


test_uuid = '5abe95ca-0bc9-4158-b51b-366156ea9448'


versions = ('2015-04-30', '2015-04-30')


@mock.patch.object(template, 'get_version', return_value=versions)
@mock.patch.object(
    template,
    'get_template_class',
    return_value=HOTemplate20150430
)
def mock_template(templ_vers, templ_class, test_templ=pool_defn):
    '''Mock a Heat template for the Kilo version.'''
    templ_dict = template_format.parse(test_templ)
    return templ_dict


def create_resource_definition(templ_dict):
    '''Create resource definition.'''
    rsrc_def = rsrc_defn.ResourceDefinition(
        'test_stack',
        templ_dict['resources']['pool']['type'],
        properties=templ_dict['resources']['pool']['properties']
    )
    return rsrc_def


@pytest.fixture
def F5LTMPool():
    '''Instantiate the F5SysiAppService resource.'''
    template_dict = mock_template()
    rsrc_def = create_resource_definition(template_dict)
    mock_stack = mock.MagicMock()
    mock_stack.resource_by_refid().get_partition_name.return_value = 'Common'
    f5_pool_obj = f5_ltm_pool.F5LTMPool(
        'testing_pool', rsrc_def, mock_stack
    )
    f5_pool_obj.uuid = test_uuid
    return f5_pool_obj


@pytest.fixture
def F5LTMPoolExists(F5LTMPool):
    F5LTMPool.get_bigip()
    mock_exists = mock.MagicMock(return_value=True)
    F5LTMPool.bigip.tm.ltm.pools.pool.exists.side_effect = mock_exists
    return F5LTMPool


@pytest.fixture
def F5LTMPoolNoExists(F5LTMPool):
    F5LTMPool.get_bigip()
    mock_exists = mock.MagicMock(return_value=False)
    F5LTMPool.bigip.tm.ltm.pools.pool.exists.side_effect = mock_exists
    return F5LTMPool


@pytest.fixture
def CreatePoolSideEffect(F5LTMPool):
    F5LTMPool.get_bigip()
    F5LTMPool.bigip.tm.ltm.pools.pool.create.side_effect = Exception()
    return F5LTMPool


@pytest.fixture
def AssignMembersSideEffect(F5LTMPool):
    F5LTMPool.get_bigip()
    F5LTMPool.bigip.tm.ltm.pools.pool.load().members_s.members.create.\
        side_effect = exception.ResourceFailure(
        mock.MagicMock(), None, action='ADD MEMBERS')
    return F5LTMPool


@pytest.fixture
def DeletePoolSideEffect(F5LTMPool):
    F5LTMPool.get_bigip()
    F5LTMPool.bigip.tm.ltm.pools.pool.load().delete.side_effect = \
        exception.ResourceFailure(mock.MagicMock(), None, action='DELETE')
    return F5LTMPool


def test_handle_create(F5LTMPool):
    create_result = F5LTMPool.handle_create()
    assert create_result is None
    assert F5LTMPool.bigip.tm.ltm.pools.pool.create.call_args == \
        mock.call(
            name=u'testing_pool',
            partition=u'Common',
            service_down_action='Reject'
        )


def test_handle_create_error(CreatePoolSideEffect):
    '''Currently, test exists to satisfy code 100% code coverage.'''
    with pytest.raises(exception.ResourceFailure):
        CreatePoolSideEffect.handle_create()


def test_handle_create_assign_members_error(AssignMembersSideEffect):
    '''Currently, test exists to satisfy code 100% code coverage.'''
    with pytest.raises(exception.ResourceFailure):
        AssignMembersSideEffect.handle_create()


def test_handle_delete(F5LTMPoolExists):
    assert F5LTMPoolExists.handle_delete() is True
    assert F5LTMPoolExists.bigip.tm.ltm.pools.pool.load.call_args == \
        mock.call(name='testing_pool', partition='Common')


def test_handle_delete_no_exists(F5LTMPoolNoExists):
    assert F5LTMPoolNoExists.handle_delete() is True


def test_handle_delete_error(DeletePoolSideEffect):
    '''Currently, test exists to satisfy code 100% code coverage.'''
    with pytest.raises(exception.ResourceFailure):
        DeletePoolSideEffect.handle_delete()


def test_resource_mapping():
    rsrc_map = f5_ltm_pool.resource_mapping()
    assert rsrc_map == {'F5::LTM::Pool': f5_ltm_pool.F5LTMPool}


def test_bad_property():
    template_dict = mock_template(test_templ=bad_pool_defn)
    rsrc_def = create_resource_definition(template_dict)
    f5_ltm_pool_obj = f5_ltm_pool.F5LTMPool(
        'test',
        rsrc_def,
        mock.MagicMock()
    )
    with pytest.raises(exception.StackValidationFailed):
        f5_ltm_pool_obj.validate()
