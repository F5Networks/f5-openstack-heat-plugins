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

from f5.bigip.bigip import BigIP
from f5_heat.resources import f5_bigip
from heat.common import exception
from heat.common import template_format
from heat.engine.hot.template import HOTemplate20150430
from heat.engine import rsrc_defn
from heat.engine import template

import mock
import pytest
import uuid

f5_bigip_defn = '''
heat_template_version: 2015-04-30
description: Testing iAppService plugin
resources:
  bigip_rsrc:
    type: F5::BigIP
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
    type: F5::BigIP
    properties:
      ip: good_ip
      username: admin
      password: admin
      bad_property: bad_prop
'''


def mock_template(test_templ=f5_bigip_defn):
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
        templ_dict['resources']['bigip_rsrc']['type'],
        properties=templ_dict['resources']['bigip_rsrc']['properties']
    )
    return rsrc_def


@pytest.fixture
def F5BigIP():
    '''Instantiate the F5BigIP resource.'''
    template_dict = mock_template()
    rsrc_def = create_resource_definition(template_dict)
    f5_bigip_obj = f5_bigip.F5BigIP(
        "testing_service", rsrc_def, mock.MagicMock()
    )
    f5_bigip_obj.validate()
    return f5_bigip_obj


# Tests

@mock.patch.object(f5_bigip.BigIP, '__init__', side_effect=Exception())
def test__init__error(mocked_bigip):
    template_dict = mock_template()
    rsrc_def = create_resource_definition(template_dict)
    with pytest.raises(Exception):
        f5_bigip.F5BigIP('test_template', rsrc_def, mock.MagicMock())


def test_handle_create(F5BigIP):
    # Set uuid on resource object because stack is mocked out
    F5BigIP.uuid = uuid.uuid4()
    create_result = F5BigIP.handle_create()
    assert create_result == None
    assert F5BigIP.resource_id is not None


def test_handle_delete(F5BigIP):
    delete_result = F5BigIP.handle_delete()
    assert delete_result == None


def test_bigip_getter(F5BigIP):
    bigip = F5BigIP.get_bigip()
    assert isinstance(bigip, BigIP)


def test_bad_property():
    template_dict = mock_template(bad_f5_bigip_defn)
    rsrc_def = create_resource_definition(template_dict)
    f5_bigip_obj = f5_bigip.F5BigIP('test', rsrc_def, mock.MagicMock())
    with pytest.raises(exception.StackValidationFailed):
        f5_bigip_obj.validate()


def test_resource_mapping():
    rsrc_map = f5_bigip.resource_mapping()
    assert rsrc_map == {
        'F5::BigIP': f5_bigip.F5BigIP
    }
