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

from f5.bigip import ManagementRoot
from f5_heat.resources import f5_bigip_device
from f5_heat.resources.f5_bigip_device import BigIPConnectionFailed
from heat.common import exception
from heat.common import template_format
from heat.engine.hot.template import HOTemplate20150430
from heat.engine import rsrc_defn
from heat.engine import template

import mock
import pytest

f5_bigip_defn = '''
heat_template_version: 2015-04-30
description: Testing iAppService plugin
resources:
  bigip_rsrc:
    type: F5::BigIP::Device
    properties:
      ip: 10.0.0.1
      username: admin
      password: admin
'''


bad_f5_bigip_defn = '''
heat_template_version: 2015-04-30
description: Testing Bad iAppService plugin
resources:
  bigip_rsrc:
    type: F5::BigIP::Device
    properties:
      ip: good_ip
      username: admin
      password: admin
      bad_property: bad_prop
'''


test_uuid = '5abe95ca-0bc9-4158-b51b-366156ea9448'

versions = ('2015-04-30', '2015-04-30')


@mock.patch.object(template, 'get_version', return_value=versions)
@mock.patch.object(
    template,
    'get_template_class',
    return_value=HOTemplate20150430
)
def mock_template(templ_vers, templ_class, test_templ=f5_bigip_defn):
    '''Mock a Heat template for the Kilo version.'''
    templ_dict = template_format.parse(test_templ)
    return templ_dict


def create_resource_definition(templ_dict):
    '''Create resource definition.'''
    rsrc_def = rsrc_defn.ResourceDefinition(
        'test_stack',
        templ_dict['resources']['bigip_rsrc']['type'],
        properties=templ_dict['resources']['bigip_rsrc']['properties']
    )
    return rsrc_def


@pytest.fixture
@mock.patch('f5_heat.resources.f5_bigip_device.ManagementRoot')
def F5BigIP(mock_mr):
    '''Instantiate the F5BigIP resource.'''
    template_dict = mock_template()
    rsrc_def = create_resource_definition(template_dict)
    f5_bigip_obj = f5_bigip_device.F5BigIPDevice(
        "testing_service", rsrc_def, mock.MagicMock()
    )
    f5_bigip_obj.uuid = test_uuid
    f5_bigip_obj.validate()
    return f5_bigip_obj


@pytest.fixture
def F5BigIPSideEffect(F5BigIP):
    F5BigIP.get_bigip = mock.MagicMock()
    return F5BigIP


@pytest.fixture
def F5BigIPHTTPError(F5BigIP):
    '''Instantiate the F5BigIP resource.'''
    mock_get_bigip = mock.MagicMock(side_effect=BigIPConnectionFailed)
    F5BigIP.get_bigip = mock_get_bigip
    return F5BigIP


# Tests

# Removed __init__ override, so removing test
@mock.patch.object(
    f5_bigip_device.ManagementRoot,
    '__init__',
    side_effect=Exception()
)
def itest__init__error(mocked_bigip):
    template_dict = mock_template()
    rsrc_def = create_resource_definition(template_dict)
    with pytest.raises(Exception):
        f5_bigip_device.F5BigIPDevice(
            'test_template',
            rsrc_def,
            mock.MagicMock()
        )


def test_handle_create(F5BigIPSideEffect):
    create_result = F5BigIPSideEffect.handle_create()
    assert create_result is None
    assert F5BigIPSideEffect.resource_id is not None


def test_handle_create_http_error(F5BigIPHTTPError):
    with pytest.raises(BigIPConnectionFailed) as ex:
        F5BigIPHTTPError.handle_create()
    assert ex.value.message == 'Failed to connect to BIG-IP device with ' \
        'message: '


def test_handle_delete(F5BigIP):
    delete_result = F5BigIP.handle_delete()
    assert delete_result is True


@mock.patch(
    'f5_heat.resources.f5_bigip_device.ManagementRoot.__init__',
    return_value=None
)
def test_bigip_getter(mock_mr_init):
    template_dict = mock_template(test_templ=bad_f5_bigip_defn)
    rsrc_def = create_resource_definition(template_dict)
    f5_bigip_obj = f5_bigip_device.F5BigIPDevice(
        'test',
        rsrc_def,
        mock.MagicMock()
    )
    bigip = f5_bigip_obj.get_bigip()
    assert isinstance(bigip, ManagementRoot)


@mock.patch('f5_heat.resources.f5_bigip_device.ManagementRoot')
def test_bad_property(mock_mr):
    template_dict = mock_template(test_templ=bad_f5_bigip_defn)
    rsrc_def = create_resource_definition(template_dict)
    f5_bigip_obj = f5_bigip_device.F5BigIPDevice(
        'test',
        rsrc_def,
        mock.MagicMock()
    )
    with pytest.raises(exception.StackValidationFailed):
        f5_bigip_obj.validate()


def test_resource_mapping():
    rsrc_map = f5_bigip_device.resource_mapping()
    assert rsrc_map == {
        'F5::BigIP::Device': f5_bigip_device.F5BigIPDevice
    }
