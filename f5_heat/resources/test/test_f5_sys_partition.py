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

from f5_heat.resources import f5_sys_partition
from heat.common import exception
from heat.common import template_format
from heat.engine.hot.template import HOTemplate20150430
from heat.engine import rsrc_defn
from heat.engine import template

import mock
import pytest

partition_defn = '''
heat_template_version: 2015-04-30
description: Testing iAppService plugin
resources:
  bigip_rsrc:
    type: F5::BigIP
    properties:
      ip: 10.0.0.1
      username: admin
      password: admin
  partition:
    type: F5::Sys::Partition
    properties:
      name: partition_test
      bigip_server: bigip_rsrc
      subpath: /
'''

bad_partition_defn = '''
heat_template_version: 2015-04-30
description: Testing iAppService plugin
resources:
  bigip_rsrc:
    type: F5::BigIP
    properties:
      ip: 10.0.0.1
      username: admin
      password: admin
  partition:
    type: F5::Sys::Partition
    properties:
      name: partition_test
      bigip_server: bigip_rsrc
      subpath: /
      bad_subpath: test_bad_subpath
'''

partition_dict = {
    'name': u'partition_test',
    'subPath': u'/',
}


versions = ('2015-04-30', '2015-04-30')


@mock.patch.object(template, 'get_version', return_value=versions)
@mock.patch.object(
    template,
    'get_template_class',
    return_value=HOTemplate20150430
)
def mock_template(templ_vers, templ_class, test_templ=partition_defn):
    '''Mock a Heat template for the Kilo version.'''
    templ_dict = template_format.parse(test_templ)
    return templ_dict


def create_resource_definition(templ_dict):
    '''Create resource definition.'''
    rsrc_def = rsrc_defn.ResourceDefinition(
        'test_stack',
        templ_dict['resources']['partition']['type'],
        properties=templ_dict['resources']['partition']['properties']
    )
    return rsrc_def


@pytest.fixture
def F5SysPartition():
    '''Instantiate the F5SysPartition resource.'''
    template_dict = mock_template()
    rsrc_def = create_resource_definition(template_dict)
    return f5_sys_partition.F5SysPartition(
        "testing_service", rsrc_def, mock.MagicMock()
    )


@pytest.fixture
def CreatePartitionSideEffect(F5SysPartition):
    F5SysPartition.get_bigip()
    F5SysPartition.bigip.tm.sys.folders.folder.create.side_effect = Exception()
    return F5SysPartition


@pytest.fixture
def DeletePartitionSideEffect(F5SysPartition):
    F5SysPartition.get_bigip()
    F5SysPartition.bigip.tm.sys.folders.folder.load.\
        side_effect = exception.ResourceFailure(
            mock.MagicMock(),
            None,
            action='Delete'
        )
    return F5SysPartition

# Tests


def test_handle_create(F5SysPartition):
    create_result = F5SysPartition.handle_create()
    assert create_result is None
    assert F5SysPartition.bigip.tm.sys.folders.folder.create.\
        call_args == mock.call(
            **partition_dict
        )


def test_handle_create_error(CreatePartitionSideEffect):
    '''Currently, test exists to satisfy 100% code coverage.'''
    with pytest.raises(exception.ResourceFailure):
        CreatePartitionSideEffect.handle_create()


def test_handle_delete(F5SysPartition):
    delete_result = F5SysPartition.handle_delete()
    assert delete_result is True
    assert F5SysPartition.bigip.tm.sys.folders.folder.load.\
        call_args == mock.call(name=u'partition_test')


def test_handle_delete_error(DeletePartitionSideEffect):
    '''Currently, test exists to satisfy 100% code coverage.'''
    with pytest.raises(exception.ResourceFailure):
        DeletePartitionSideEffect.handle_delete()


def test_get_partition_name(F5SysPartition):
    partition_name = F5SysPartition.get_partition_name()
    assert partition_name == 'partition_test'


def test_resource_mapping():
    rsrc_map = f5_sys_partition.resource_mapping()
    assert rsrc_map == {
        'F5::Sys::Partition': f5_sys_partition.F5SysPartition
    }
