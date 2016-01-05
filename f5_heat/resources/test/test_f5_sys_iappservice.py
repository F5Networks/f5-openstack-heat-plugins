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

from f5.bigip import BigIP
from f5_heat.resources import f5_sys_iappservice
from heat.common import exception
from heat.common import template_format
from heat.engine.hot.template import HOTemplate20150430
from heat.engine import rsrc_defn
from heat.engine import stack
from heat.engine import template
from heat.tests import utils

import inspect
import mock
import pytest


iapp_service_defn = '''
heat_template_version: 2015-04-30
description: Testing iAppService plugin
resources:
  iapp_service:
    type: F5::Sys::iAppService
    properties:
      name: testing
      bigip_server: abc.host
      bigip_username: admin
      bigip_password: admin
      template_name: testing_template
'''


iapp_service_dict = {
    'name': u'testing',
    'template': '/Common/testing_template'
}


def mock_template():
    '''Mock a Heat template for the Kilo version.'''
    versions = ('2015-04-30', '2015-04-30')
    template.get_version = mock.Mock(return_value=versions)
    template.get_template_class = mock.Mock(return_value=HOTemplate20150430)
    templ_dict = template_format.parse(iapp_service_defn)
    return templ_dict, template.Template(templ_dict)


def mock_stack(templ_dict, templ):
    '''Create a partially mocked Heat stack for use in creating a resource.'''
    stk = stack.Stack(utils.dummy_context(), 'test_stack', templ)
    rsrc_def = rsrc_defn.ResourceDefinition(
        'test_stack',
        templ_dict['resources']['iapp_service']['type'],
        properties=templ_dict['resources']['iapp_service']['properties']
    )
    return rsrc_def, stk


@pytest.fixture
@mock.patch('f5_heat.resources.f5_sys_iappservice.BigIP')
def F5SysiAppService(mocked_bigip):
    '''Instantiate the F5SysiAppService resource with a mocked BigIP.'''
    template_dict, template = mock_template()
    rsrc_def, stk = mock_stack(template_dict, template)
    return f5_sys_iappservice.F5SysiAppService(
        "iapp_template", rsrc_def, stk
    )


@pytest.fixture
def CreateServiceSideEffect(F5SysiAppService):
    F5SysiAppService.bigip.sys.iapp.create_service.side_effect = \
        Exception()
    return F5SysiAppService


@pytest.fixture
def DeleteServiceSideEffect(F5SysiAppService):
    F5SysiAppService.bigip.sys.iapp.delete_service.side_effect = \
        Exception()
    return F5SysiAppService

# Tests


@mock.patch.object(
    f5_sys_iappservice.BigIP,
    '__init__',
    side_effect=Exception()
)
def test__init__error(mocked_init):
    template_dict, template = mock_template()
    rsrc_def, stk = mock_stack(template_dict, template)
    with pytest.raises(Exception):
        f5_sys_iappservice.F5SysiAppService(
            "iapp_template", rsrc_def, stk
        )


def test_handle_create(F5SysiAppService):
    create_result = F5SysiAppService.handle_create()
    assert create_result == None
    assert F5SysiAppService.bigip.sys.iapp.create_service.call_args == \
        mock.call(
            name=u'testing',
            service=iapp_service_dict
        )


def test_handle_create_error(CreateServiceSideEffect):
    with pytest.raises(exception.ResourceFailure):
        CreateServiceSideEffect.handle_create()


def test_handle_delete(F5SysiAppService):
    delete_result = F5SysiAppService.handle_delete()
    assert delete_result == None
    assert F5SysiAppService.bigip.sys.iapp.delete_service.call_args == \
        mock.call(name=u'testing')


def test_handle_delete_error(DeleteServiceSideEffect):
    with pytest.raises(exception.ResourceFailure):
        DeleteServiceSideEffect.handle_delete()


def test_resource_mapping():
    rsrc_map = f5_sys_iappservice.resource_mapping()
    assert rsrc_map == {
        'F5::Sys::iAppService': f5_sys_iappservice.F5SysiAppService
    }


# The test below shows that the BigIP object and init method is no longer
# mocked.

def test_suite_metatest():
    assert f5_sys_iappservice.BigIP is BigIP
    assert True == inspect.ismethod(f5_sys_iappservice.BigIP.__init__)
