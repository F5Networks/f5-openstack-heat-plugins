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

from f5_heat.resources import f5_cm_sync
from heat.common import exception
from heat.common import template_format
from heat.engine.hot.template import HOTemplate20150430
from heat.engine import rsrc_defn
from heat.engine import template

import mock
import pytest

save_defn = '''
heat_template_version: 2015-04-30
resources:
  bigip_rsrc:
    type: F5::BigIP::Device
    properties:
      ip: 10.0.0.1
      username: admin
      password: admin
  sync_rsrc:
    type: F5::Cm::Sync
    properties:
      bigip_server: bigip_rsrc
      device_group: dg
      device_group_partition: partition
'''


sync_status = \
    {'https://localhost/mgmt/tm/cm/sync-status/0':
     {'nestedStats':
      {'entries':
       {'status':
        {'description': None}
        }
       }
      }
     }


class SyncStatusEntries(object):
    def __init__(self, status):
        self.entries = sync_status
        (self.entries['https://localhost/mgmt/tm/cm/sync-status/0']
         ['nestedStats']['entries']['status']['description']) = status

    def refresh(self):
        pass


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
        templ_dict['resources']['sync_rsrc']['type'],
        properties=templ_dict['resources']['sync_rsrc']['properties']
    )
    return rsrc_def


@pytest.fixture
def F5CmSync():
    '''Instantiate the F5CmSync resource'''
    template_dict = mock_template()
    rsrc_def = create_resource_definition(template_dict)
    return f5_cm_sync.F5CmSync(
        "testing_sync", rsrc_def, mock.MagicMock()
    )


@pytest.fixture
def CreateSyncDGNonExtant(F5CmSync):
    F5CmSync.get_bigip()
    F5CmSync.bigip.tm.cm.device_groups.device_group.exists.side_effect = \
        Exception('test')
    return F5CmSync


@pytest.fixture
def CreateSyncSyncFails(F5CmSync):
    F5CmSync.get_bigip()
    F5CmSync.bigip.tm.cm.exec_cmd.side_effect = Exception('test')
    return F5CmSync


# Tests


def test_handle_create(F5CmSync):
    create_result = F5CmSync.handle_create()
    assert create_result is None
    assert F5CmSync.bigip.tm.cm.device_groups.device_group.exists.call_args \
        == mock.call(name='dg', partition='partition')


def test_handle_create_error_dg_non_extant(CreateSyncDGNonExtant):
    '''Currently, test exists to satisfy 100% code coverage.'''
    with pytest.raises(exception.ResourceFailure) as ex:
        CreateSyncDGNonExtant.handle_create()
    assert 'test' in ex.value.message


def test_handle_create_error_sync_fails(CreateSyncSyncFails):
    '''Currently, test exists to satisfy 100% code coverage.'''
    with pytest.raises(exception.ResourceFailure) as ex:
        CreateSyncSyncFails.handle_create()
    assert 'test' in ex.value.message


def test_handle_check_create_complete_true(F5CmSync):
    F5CmSync.get_bigip()
    F5CmSync.bigip.tm.cm.sync_status = SyncStatusEntries('In Sync')
    check_result = F5CmSync.check_create_complete('token')
    assert check_result is True


def test_handle_check_create_complete_false(F5CmSync):
    F5CmSync.get_bigip()
    F5CmSync.bigip.tm.cm.sync_status = SyncStatusEntries('disconnected')
    check_result = F5CmSync.check_create_complete('token')
    assert check_result is False


def test_handle_delete(F5CmSync):
    delete_result = F5CmSync.handle_delete()
    assert delete_result is True


def test_resource_mapping():
    rsrc_map = f5_cm_sync.resource_mapping()
    assert rsrc_map == {
        'F5::Cm::Sync': f5_cm_sync.F5CmSync
    }
