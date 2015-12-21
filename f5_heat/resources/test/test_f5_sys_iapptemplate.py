# Copyright 2015 F5 Networks Inc.
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

from f5_heat.resources import f5_sys_iapptemplate
from heat.common import exception
from heat.common import template_format
from heat.engine.hot.template import HOTemplate20150430
from heat.engine import rsrc_defn
from heat.engine import stack
from heat.engine import template
from heat.tests import utils

import mock
import pytest


iapp_template_defn = '''
heat_template_version: 2015-04-30
description: Testing iAppTemplate plugin
resources:
    iapp_template:
        type: F5::Sys::iAppTemplate
        properties:
          name: testing_template
          bigip_server: bigip.abc.com
          bigip_username: admin
          bigip_password: password
          requires_modules: [ ltm ]
          implementation: |
            hello
          presentation: |
            hello
'''

iapp_actions_dict = {
    'name': u'testing_template',
    'actions': {
        'definition': {
            'implementation': u'hello\n',
            'presentation': u'hello\n',
        }
    },
    'requiresModules': [u'ltm']
}


def mock_template():
    '''Mock a Heat template for the Kilo version.'''
    versions = ('2015-04-30', '2015-04-30')
    template.get_version = mock.Mock(return_value=versions)
    template.get_template_class = mock.Mock(return_value=HOTemplate20150430)
    templ_dict = template_format.parse(iapp_template_defn)
    return templ_dict, template.Template(templ_dict)


def mock_stack(templ_dict, templ):
    '''Create a partially mocked Heat stack for use in creating a resource.'''
    stk = stack.Stack(utils.dummy_context(), 'test_stack', templ)
    rsrc_def = rsrc_defn.ResourceDefinition(
        'test_stack',
        templ_dict['resources']['iapp_template']['type'],
        properties=templ_dict['resources']['iapp_template']['properties']
    )
    return rsrc_def, stk


@pytest.fixture
def F5SysiAppTemplate():
    '''Instantiate the F5SysiAppTemplate resource with a mocked BigIP.'''
    f5_sys_iapptemplate.BigIP = mock.Mock()
    template_dict, template = mock_template()
    rsrc_def, stk = mock_stack(template_dict, template)
    return f5_sys_iapptemplate.F5SysiAppTemplate(
        "iapp_template", rsrc_def, stk
    )


def test__init__error():
    f5_sys_iapptemplate.BigIP.__init__ = mock.Mock(side_effect=Exception())
    template_dict, template = mock_template()
    rsrc_def, stk = mock_stack(template_dict, template)
    with pytest.raises(Exception):
        f5_sys_iapptemplate.F5SysiAppTemplate(
            "iapp_template", rsrc_def, stk
        )


class TestCreate(object):
    def test_handle_create(self, F5SysiAppTemplate):
        template_dict, template = mock_template()
        create_result = F5SysiAppTemplate.handle_create()
        assert create_result == None
        assert F5SysiAppTemplate.bigip.sys.iapp.create_template.call_args == \
            mock.call(
                name=u'testing_template',
                template=iapp_actions_dict
            )

    def test_handle_create_error(self, F5SysiAppTemplate):
        F5SysiAppTemplate.bigip.sys.iapp.create_template.side_effect = \
            Exception()
        with pytest.raises(exception.ResourceFailure):
                F5SysiAppTemplate.handle_create()


class TestDelete(object):
    def test_handle_delete(self, F5SysiAppTemplate):
        delete_result = F5SysiAppTemplate.handle_delete()
        assert delete_result == None
        assert F5SysiAppTemplate.bigip.sys.iapp.delete_template.call_args == \
            mock.call('testing_template')

    def test_handle_delete_error(self, F5SysiAppTemplate):
        F5SysiAppTemplate.bigip.sys.iapp.delete_template.side_effect = \
            Exception()
        with pytest.raises(exception.ResourceFailure):
            F5SysiAppTemplate.handle_delete()


def test_resource_mapping():
    rsrc_map = f5_sys_iapptemplate.resource_mapping()
    assert rsrc_map == {
        'F5::Sys::iAppTemplate': f5_sys_iapptemplate.F5SysiAppTemplate
    }
