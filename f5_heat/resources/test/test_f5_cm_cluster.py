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

from f5.sdk_exception import F5SDKError
from f5_heat.resources import f5_cm_cluster
from heat.common.exception import ResourceFailure
from heat.common import template_format
from heat.engine.hot.template import HOTemplate20150430
from heat.engine import rsrc_defn
from heat.engine import template

import mock
import pytest


cluster_template_defn = '''
heat_template_version: 2015-04-30
description: Testing clustering tempalte
resources:
  bigip_rsrc1:
    type: F5::BigIP::Device
    properties:
      ip: 10.0.0.1
      username: admin
      password: admin
  bigip_rsrc2:
    type: F5::BigIP::Device
    properties:
      ip: 10.0.0.2
      username: admin
      password: admin
  bigip_rsrc3:
    type: F5::BigIP::Device
    properties:
      ip: 10.0.0.3
      username: admin
      password: admin
  cluster:
    type: F5::Cm::Cluster
    properties:
      device_group_name: test_cluster
      devices: [bigip_rsrc1, bigip_rsrc2, bigip_rsrc3]
      device_group_partition: Common
      device_group_type: sync-failover
'''


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
        test_templ=cluster_template_defn
):
    '''Mock a Heat template for the Kilo version.'''
    templ_dict = template_format.parse(test_templ)
    return templ_dict


def create_resource_definition(templ_dict):
    '''Create a resource definition.'''
    rsrc_def = rsrc_defn.ResourceDefinition(
        'test_stack',
        templ_dict['resources']['cluster']['type'],
        properties=templ_dict['resources']['cluster']['properties']
    )
    return rsrc_def


@pytest.fixture
def F5CmCluster():
    '''Instantiate the F5CmCluster resource.'''
    template_dict = mock_template()
    rsrc_def = create_resource_definition(template_dict)
    f5_cm_cluster.ClusterManager.__init__ = mock.MagicMock(return_value=None)
    f5_cm_cluster.ClusterManager.create = mock.MagicMock()
    f5_cm_cluster.ClusterManager.teardown = mock.MagicMock()
    mock_bigip = mock.MagicMock(name='fake-bigip')
    mock_stack = mock.MagicMock(name='fake-stack')
    cluster = f5_cm_cluster.F5CmCluster(
        "cluster", rsrc_def, mock_stack
    )
    cluster.stack.resource_by_refid().get_bigip.return_value = mock_bigip
    return cluster, mock_bigip


@pytest.fixture
def ClusterMgrF5SDKError():
    template_dict = mock_template()
    rsrc_def = create_resource_definition(template_dict)
    f5_cm_cluster.ClusterManager.__init__ = mock.MagicMock()
    f5_cm_cluster.ClusterManager.__init__.side_effect = ResourceFailure(
        F5SDKError('test'), None, action='Create'
    )
    return f5_cm_cluster.F5CmCluster(
        "cluster", rsrc_def, mock.MagicMock()
    )


# Tests


def test_handle_create(F5CmCluster):
    cluster, mock_bigip = F5CmCluster
    create_result = cluster.handle_create()
    assert create_result is None
    assert f5_cm_cluster.ClusterManager.create.call_args == \
        mock.call(
            devices=[mock_bigip, mock_bigip, mock_bigip],
            device_group_name='test_cluster',
            device_group_partition='Common',
            device_group_type='sync-failover'
        )


def test_handle_create_fdsdkerror(ClusterMgrF5SDKError):
    with pytest.raises(ResourceFailure) as ex:
        ClusterMgrF5SDKError.handle_create()
    assert 'F5SDKError: test' in ex.value.message


def test_handle_delete(F5CmCluster):
    cluster, mock_bigip = F5CmCluster
    create_result = cluster.handle_delete()
    assert create_result is True
    assert f5_cm_cluster.ClusterManager.__init__.call_args == \
        mock.call(
            devices=[mock_bigip, mock_bigip, mock_bigip],
            device_group_name='test_cluster',
            device_group_partition='Common',
            device_group_type='sync-failover'
        )
    assert f5_cm_cluster.ClusterManager.teardown.call_args == mock.call()


def test_handle_delete_f5sdkerror(ClusterMgrF5SDKError):
    with pytest.raises(ResourceFailure) as ex:
        ClusterMgrF5SDKError.handle_delete()
    assert 'F5SDKError: test' in ex.value.message


def test_resource_mapping():
    rsrc_map = f5_cm_cluster.resource_mapping()
    assert rsrc_map == {'F5::Cm::Cluster': f5_cm_cluster.F5CmCluster}
