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

from common.f5_bigip_connection import F5BigIPMixin
from oslo_log import log as logging

import json

LOG = logging.getLogger(__name__)


class F5SysiAppService(resource.Resource, F5BigIPMixin):
    '''Manages creation of an iApp resource on the BigIP device.'''

    PROPERTIES = (
        NAME,
        BIGIP_SERVER,
        TEMPLATE_NAME,
        VARIABLES,
        LISTS,
        TABLES
    ) = (
        'name',
        'bigip_server',
        'template_name',
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
            _('IP address of BigIP device.'),
            required=True
        ),
        TEMPLATE_NAME: properties.Schema(
            properties.Schema.STRING,
            _('Template to use when creating the service.'),
            required=True
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

        self.app_answers = {}
        for prop in [self.VARIABLES, self.LISTS, self.TABLES]:
            if self.properties[prop] is not None:
                self.validate_app_answers(prop)

    def validate_app_answers(self, prop_name):
        '''Load a property as json.

        :param prop_name: name of property to load
        :raises: KeyError, ValueError, TypeError
        '''

        try:
            self.app_answers[prop_name] = json.loads(
                self.properties[prop_name]
            )
        except Exception:
            LOG.error(
                _LE("'%s' property failed to parse as JSON") % prop_name
            )
            raise

    def build_service_dict(self):
        '''Builds a dictionary of service configuration.'''

        service_dict = {
            'name': self.properties[self.NAME],
            'template': '/Common/{}'.format(
                self.properties[self.TEMPLATE_NAME]
            )
        }
        service_dict.update(self.app_answers)
        return service_dict

    def handle_create(self):
        '''Creates the iApp Service from an iApp template.

        :raises: ResourceFailure # TODO Change to proper exception
        '''

        self.get_bigip()
        service_dict = self.build_service_dict()

        try:
            self.bigip.iapp.create_service(
                name=self.properties[self.NAME],
                service=service_dict
            )
        except Exception as ex:
            raise exception.ResourceFailure(ex, None, action='CREATE')

    def handle_delete(self):
        '''Deletes the iApp Service

        :raises: Resource Failure # TODO Change to proper exception
        '''

        self.get_bigip()

        try:
            self.bigip.iapp.delete_service(
                name=self.properties[self.NAME]
            )
        except Exception as ex:
            raise exception.ResourceFailure(ex, None, action='DELETE')


def resource_mapping():
    return {'F5::Sys::iAppService': F5SysiAppService}
