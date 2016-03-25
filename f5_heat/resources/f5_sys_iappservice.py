# coding=utf-8
#
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


from heat.common import exception
from heat.common.i18n import _
from heat.common.i18n import _LE
from heat.engine import properties
from heat.engine import resource

from common.mixins import f5_common_resources
from common.mixins import F5BigIPMixin
from oslo_log import log as logging

import json

LOG = logging.getLogger(__name__)


class F5SysiAppService(resource.Resource, F5BigIPMixin):
    '''Manages creation of an iApp® resource on the BIG-IP®.'''

    PROPERTIES = (
        NAME,
        BIGIP_SERVER,
        PARTITION,
        TEMPLATE_NAME,
        TRAFFIC_GROUP,
        VARIABLES,
        LISTS,
        TABLES
    ) = (
        'name',
        'bigip_server',
        'partition',
        'template_name',
        'traffic_group',
        'variables',
        'lists',
        'tables'
    )

    properties_schema = {
        NAME: properties.Schema(
            properties.Schema.STRING,
            _('Name of the template.'),
            required=True
        ),
        BIGIP_SERVER: properties.Schema(
            properties.Schema.STRING,
            _('IP address of BigIP device.')
        ),
        PARTITION: properties.Schema(
            properties.Schema.STRING,
            _('Partition resource reference.'),
            required=True
        ),
        TEMPLATE_NAME: properties.Schema(
            properties.Schema.STRING,
            _('Template to use when creating the service.'),
            required=True
        ),
        TRAFFIC_GROUP: properties.Schema(
            properties.Schema.STRING,
            _('Traffic group for this service.')
        ),
        VARIABLES: properties.Schema(
            properties.Schema.STRING,
            _('JSON formatted list of variables for the service.')
        ),
        LISTS: properties.Schema(
            properties.Schema.STRING,
            _('JSON formatted list of lists of variables.')
        ),
        TABLES: properties.Schema(
            properties.Schema.STRING,
            _('JSON formatted list of tables for the service.')
        )
    }

    def __init__(self, name, defn, stack):
        '''Call super and validate answer properties.'''
        super(F5SysiAppService, self).__init__(name, defn, stack)

        self.iapp_answers_from_hot = {}
        for prop in [self.VARIABLES, self.LISTS, self.TABLES]:
            if self.properties[prop] is not None:
                self._check_iapp_answers(prop)

    def _check_iapp_answers(self, prop_name):
        '''Load a property as json.

        :param prop_name: name of property to load
        :raises: KeyError, ValueError, TypeError
        '''

        try:
            self.iapp_answers_from_hot[prop_name] = json.loads(
                self.properties[prop_name]
            )
        except Exception:
            LOG.error(
                _LE("'%s' property failed to parse as JSON") % prop_name
            )
            raise

    def _build_service_dict(self):
        '''Builds a dictionary of service configuration.'''

        service_dict = {
            'name': self.properties[self.NAME],
            'template': self.properties[self.TEMPLATE_NAME]
        }

        if self.properties[self.TRAFFIC_GROUP]:
            service_dict['trafficGroup'] = self.properties[self.TRAFFIC_GROUP]
        service_dict.update(self.iapp_answers_from_hot)
        return service_dict

    @f5_common_resources
    def handle_create(self):
        '''Creates the iApp® Service from an iApp® template.

        :raises: ResourceFailure # TODO Change to proper exception
        '''

        service_dict = self._build_service_dict()
        service_dict['partition'] = self.partition_name

        try:
            service = self.bigip.sys.applications.services.service
            service.create(**service_dict)
        except Exception as ex:
            raise exception.ResourceFailure(ex, None, action='CREATE')

    @f5_common_resources
    def handle_delete(self):
        '''Deletes the iApp® Service

        :raises: Resource Failure # TODO Change to proper exception
        '''

        if self.bigip.sys.applications.services.service.exists(
                name=self.properties[self.NAME],
                partition=self.partition_name
        ):
            try:
                loaded_service = \
                    self.bigip.sys.applications.services.service.load(
                        name=self.properties[self.NAME],
                        partition=self.partition_name
                    )
                loaded_service.delete()
            except Exception as ex:
                raise exception.ResourceFailure(ex, None, action='DELETE')
        return True


def resource_mapping():
    return {'F5::Sys::iAppService': F5SysiAppService}
