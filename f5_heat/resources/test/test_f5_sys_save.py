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

from f5_heat.resources import f5_sys_save
from heat.common import exception
from heat.common import template_format
from heat.engine.hot.template import HOTemplate20150430
from heat.engine import rsrc_defn
from heat.engine import template

import mock
import pytest

save_defn = '''
heat_template_version: 2015-04-30
description: Testing iAppService plugin
resources:
  bigip_rsrc:
    type: F5::BigIP::Device
    properties:
      ip: 10.0.0.1
      username: admin
      password: admin
  save_rsrc:
    type: F5::Sys::Save
    properties:
      bigip_server: bigip_rsrc
'''


versions = ('2015-04-30', '2015-04-30')


@mock.patch.object(template, 'get_version', return_value=versions)
@mock.patch.object(
    template,
    'get_template_class',
    return_value=HOTemplate20150430
)
def mock_template(templ_vers, templ_class, test_templ=save_defn):
    '''Mock a Heat template for the Kilo version.'''
    templ_dict = template_format.parse(test_templ)
    return templ_dict


def create_resource_definition(templ_dict):
    '''Create resource definition.'''
    rsrc_def = rsrc_defn.ResourceDefinition(
        'test_stack',
        templ_dict['resources']['save_rsrc']['type'],
        properties=templ_dict['resources']['save_rsrc']['properties']
    )
    return rsrc_def


@pytest.fixture
def F5SysSave():
    '''Instantiate the F5SysSave resource.'''
    template_dict = mock_template()
    rsrc_def = create_resource_definition(template_dict)
    return f5_sys_save.F5SysSave(
        "testing_save", rsrc_def, mock.MagicMock()
    )


@pytest.fixture
def CreateSaveSideEffect(F5SysSave):
    F5SysSave.get_bigip()
    F5SysSave.bigip.tm.sys.config.exec_cmd.side_effect = Exception()
    return F5SysSave


# Tests


def test_handle_create(F5SysSave):
    create_result = F5SysSave.handle_create()
    assert create_result is None
    assert F5SysSave.bigip.tm.sys.config.exec_cmd.call_args == \
        mock.call('save')


def test_handle_create_error(CreateSaveSideEffect):
    '''Currently, test exists to satisfy 100% code coverage.'''
    with pytest.raises(exception.ResourceFailure):
        CreateSaveSideEffect.handle_create()


def test_handle_delete(F5SysSave):
    delete_result = F5SysSave.handle_delete()
    assert delete_result is True


def test_resource_mapping():
    rsrc_map = f5_sys_save.resource_mapping()
    assert rsrc_map == {
        'F5::Sys::Save': f5_sys_save.F5SysSave
    }
