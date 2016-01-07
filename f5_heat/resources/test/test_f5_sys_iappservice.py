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

from f5_heat.resources import f5_sys_iappservice
from heat.common import exception
from heat.common import template_format
from heat.engine.hot.template import HOTemplate20150430
from heat.engine import rsrc_defn
from heat.engine import template

import mock
import pytest

iapp_service_defn = '''
heat_template_version: 2015-04-30
description: Testing iAppService plugin
resources:
  bigip_rsrc:
    type: F5::BigIP
    properties:
      ip: 10.0.0.1
      username: admin
      password: admin
  iapp_service:
    type: F5::Sys::iAppService
    properties:
      name: testing_service
      bigip_server: bigip_rsrc
      template_name: testing_template
'''

bad_iapp_service_defn = '''
heat_template_version: 2015-04-30
description: Testing iAppService plugin
resources:
  bigip_rsrc:
    type: F5::BigIP
    properties:
      ip: 10.0.0.1
      username: admin
      password: admin
  iapp_service:
    type: F5::Sys::iAppService
    properties:
      bigip_server: bigip_rsrc
      template_name: testing_template
'''

iapp_service_dict = {
    'name': u'testing_service',
    'template': '/Common/testing_template'
}


def mock_template(test_templ=iapp_service_defn):
    '''Mock a Heat template for the Kilo version.'''
    versions = ('2015-04-30', '2015-04-30')
    template.get_version = mock.Mock(return_value=versions)
    template.get_template_class = mock.Mock(return_value=HOTemplate20150430)
    templ_dict = template_format.parse(test_templ)
    return templ_dict


def create_resource_definition(templ_dict):
    '''Create resource definition.'''
    rsrc_def = rsrc_defn.ResourceDefinition(
        'test_stack',
        templ_dict['resources']['iapp_service']['type'],
        properties=templ_dict['resources']['iapp_service']['properties']
    )
    return rsrc_def


@pytest.fixture
def F5SysiAppService():
    '''Instantiate the F5SysiAppService resource.'''
    template_dict = mock_template()
    rsrc_def = create_resource_definition(template_dict)
    return f5_sys_iappservice.F5SysiAppService(
        "testing_service", rsrc_def, mock.MagicMock()
    )


@pytest.fixture
def CreateServiceSideEffect(F5SysiAppService):
    F5SysiAppService.get_bigip()
    F5SysiAppService.bigip.iapp.create_service.side_effect = \
        Exception()
    return F5SysiAppService


@pytest.fixture
def DeleteServiceSideEffect(F5SysiAppService):
    F5SysiAppService.get_bigip()
    F5SysiAppService.bigip.iapp.delete_service.side_effect = \
        Exception()
    return F5SysiAppService

# Tests


def test_handle_create(F5SysiAppService):
    create_result = F5SysiAppService.handle_create()
    assert create_result == None
    assert F5SysiAppService.bigip.iapp.create_service.call_args == \
        mock.call(
            name=u'testing_service',
            service=iapp_service_dict
        )


def test_handle_create_error(CreateServiceSideEffect):
    with pytest.raises(exception.ResourceFailure):
        CreateServiceSideEffect.handle_create()


def test_handle_delete(F5SysiAppService):
    delete_result = F5SysiAppService.handle_delete()
    assert delete_result == None
    assert F5SysiAppService.bigip.iapp.delete_service.call_args == \
        mock.call(name=u'testing_service')


def test_handle_delete_error(DeleteServiceSideEffect):
    with pytest.raises(exception.ResourceFailure):
        DeleteServiceSideEffect.handle_delete()


def test_resource_mapping():
    rsrc_map = f5_sys_iappservice.resource_mapping()
    assert rsrc_map == {
        'F5::Sys::iAppService': f5_sys_iappservice.F5SysiAppService
    }


def test_bad_property():
    template_dict = mock_template(bad_iapp_service_defn)
    rsrc_def = create_resource_definition(template_dict)
    f5_sys_iappservice_obj = f5_sys_iappservice.F5SysiAppService(
        'test',
        rsrc_def,
        mock.MagicMock()
    )
    with pytest.raises(exception.StackValidationFailed):
        f5_sys_iappservice_obj.validate()
