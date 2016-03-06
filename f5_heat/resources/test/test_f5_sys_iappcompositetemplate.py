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

from f5_heat.resources import f5_sys_iappcompositetemplate
from heat.common import exception
from heat.common import template_format
from heat.engine.hot.template import HOTemplate20150430
from heat.engine import rsrc_defn
from heat.engine import template

import mock
import pytest


iapp_composite_template_defn = '''
heat_template_version: 2015-04-30
description: Testing iAppCompositeTemplate plugin
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
  iapp_template:
    type: F5::Sys::iAppCompositeTemplate
    depends_on: bigip_rsrc
    properties:
      name: testing_template
      bigip_server: bigip_rsrc
      partition: partition
      requires_modules: [ ltm ]
      implementation: hello
      presentation: hello
      role-acl: [ admin, user ]
'''


bad_iapp_template_defn = '''
heat_template_version: 2015-04-30
description: Testing iAppTemplate plugin
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
      name: Common
      bigip_server: bigip_rsrc
  iapp_template:
    type: F5::Sys::iAppTemplate
    depends_on: bigip_rsrc
    properties:
      name: testing_template
      partition: partition
      bigip_server: bigip_rsrc
      requires_modules: not_a_list
      bad_iplementation: |
        hello
      presentation: |
        hello
'''

iapp_actions_dict = {
    'name': u'testing_template',
    'partition': u'Common',
    'requiresModules': [u'ltm'],
    'actions': {
        'definition': {
            u'implementation': u'hello',
            u'presentation': u'hello',
            u'roleAcl': [u'admin', u'user']
        }
    },
}


versions = ('2015-04-30', '2015-04-30')


@mock.patch.object(template, 'get_version', return_value=versions)
@mock.patch.object(
    template,
    'get_template_class',
    return_value=HOTemplate20150430
)
def mock_template(
        templ_vers,
        templ_class,
        test_templ=iapp_composite_template_defn
):
    '''Mock a Heat template for the Kilo version.'''
    templ_dict = template_format.parse(test_templ)
    return templ_dict


def create_resource_definition(templ_dict):
    '''Create a resource definition.'''
    rsrc_def = rsrc_defn.ResourceDefinition(
        'test_stack',
        templ_dict['resources']['iapp_template']['type'],
        properties=templ_dict['resources']['iapp_template']['properties']
    )
    return rsrc_def


@pytest.fixture
def F5SysiAppTemplate():
    '''Instantiate the F5SysiAppTemplate resource.'''
    template_dict = mock_template()
    rsrc_def = create_resource_definition(template_dict)
    mock_stack = mock.MagicMock()
    mock_stack.resource_by_refid().get_partition_name.return_value = 'Common'
    return f5_sys_iappcompositetemplate.F5SysiAppCompositeTemplate(
        "iapp_template", rsrc_def, mock_stack
    )


@pytest.fixture
def CreateTemplateSideEffect(F5SysiAppTemplate):
    F5SysiAppTemplate.get_bigip()
    F5SysiAppTemplate.bigip.sys.applications.templates.template.create.\
        side_effect = exception.ResourceFailure(
            mock.MagicMock(),
            None,
            action='CREATE'
        )
    return F5SysiAppTemplate


@pytest.fixture
def DeleteTemplateSideEffect(F5SysiAppTemplate):
    F5SysiAppTemplate.get_bigip()
    F5SysiAppTemplate.bigip.sys.applications.templates.template.load.\
        side_effect = exception.ResourceFailure(
            mock.MagicMock(),
            None,
            action='DELETE'
        )
    return F5SysiAppTemplate

# Tests


def test_handle_create(F5SysiAppTemplate):
    create_result = F5SysiAppTemplate.handle_create()
    assert create_result is None
    assert F5SysiAppTemplate.bigip.sys.applications.templates.template.create.\
        call_args == mock.call(**iapp_actions_dict)


def test_handle_create_error(CreateTemplateSideEffect):
    '''Currently, test exists to satisfy 100% code coverage.'''
    with pytest.raises(exception.ResourceFailure):
        CreateTemplateSideEffect.handle_create()


def test_handle_delete(F5SysiAppTemplate):
    delete_result = F5SysiAppTemplate.handle_delete()
    assert delete_result is None
    assert F5SysiAppTemplate.bigip.sys.applications.templates.template.load.\
        call_args == mock.call(name='testing_template', partition='Common')


def test_handle_delete_error(DeleteTemplateSideEffect):
    '''Currently, test exists to satisfy 100% code coverage.'''
    with pytest.raises(exception.ResourceFailure):
        DeleteTemplateSideEffect.handle_delete()


def test_resource_mapping():
    rsrc_map = f5_sys_iappcompositetemplate.resource_mapping()
    assert rsrc_map == {
        'F5::Sys::iAppCompositeTemplate':
        f5_sys_iappcompositetemplate.F5SysiAppCompositeTemplate
    }


def test_bad_property():
    template_dict = mock_template(test_templ=bad_iapp_template_defn)
    rsrc_def = create_resource_definition(template_dict)
    f5_sys_iapptemplate_obj = \
        f5_sys_iappcompositetemplate.F5SysiAppCompositeTemplate(
            'test',
            rsrc_def,
            mock.MagicMock()
        )
    with pytest.raises(exception.StackValidationFailed):
        f5_sys_iapptemplate_obj.validate()
