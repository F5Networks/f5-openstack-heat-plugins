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
from heat.engine import properties
from heat.engine import resource


class F5SysiAppService(resource.Resource):
    '''Manages creation of an iApp resource on the BigIP device.'''

    PROPERTIES = (
        NAME,
        BIGIP_SERVER,
        TEMPLATE_NAME
    ) = (
        'name',
        'bigip_server',
        'template_name'
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
        )
    }

    def get_bigip(self):
        '''Retrieve the BigIP connection from the F5::BigIP resource.'''
        refid = self.properties[self.BIGIP_SERVER]
        self.bigip = self.stack.resource_by_refid(refid).get_bigip()

    def handle_create(self):
        '''Creates the iApp Service from an iApp template.

        :raises: ResourceFailure # TODO Change to proper exception
        '''

        self.get_bigip()

        template_dict = {
            'name': self.properties[self.NAME],
            'template': '/Common/{}'.format(
                self.properties[self.TEMPLATE_NAME]
            )
        }
        try:
            self.bigip.iapp.create_service(
                name=self.properties[self.NAME],
                service=template_dict
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
