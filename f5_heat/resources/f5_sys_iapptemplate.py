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

from common.f5_bigip_connection import F5BigIPConnection


class F5SysiAppTemplate(resource.Resource, F5BigIPConnection):
    '''Manages creation of an iApp resource on the BigIP device.'''

    PROPERTIES = (
        NAME,
        BIGIP_SERVER,
        REQUIRES_MODULES,
        IMPLEMENTATION,
        PRESENTATION,
        HELP
    ) = (
        'name',
        'bigip_server',
        'requires_modules',
        'implementation',
        'presentation',
        'help'
    )

    properties_schema = {
        NAME: properties.Schema(
            properties.Schema.STRING,
            _('Name of the template.'),
            required=True
        ),
        BIGIP_SERVER: properties.Schema(
            properties.Schema.STRING,
            _('BigIP resource reference.'),
            required=True
        ),
        REQUIRES_MODULES: properties.Schema(
            properties.Schema.LIST,
            _('Modules required for this iApp Template.')
        ),
        IMPLEMENTATION: properties.Schema(
            properties.Schema.STRING,
            _('Implementation section of the template.'),
            required=True
        ),
        PRESENTATION: properties.Schema(
            properties.Schema.STRING,
            _('Presentation section of the template.'),
            required=True
        ),
        HELP: properties.Schema(
            properties.Schema.STRING,
            _('Help section of the template.'),
        )
    }

    def build_iapp_dict(self):
        '''Build dictionary for posting to BigIP.

        :returns: dictionary of template information
        '''

        sections = {
            'implementation': self.properties[self.IMPLEMENTATION] or '',
            'presentation': self.properties[self.PRESENTATION] or ''
        }
        definition = {'definition': sections}
        template = {
            'name': self.properties[self.NAME],
            'actions': definition,
            'requiresModules': self.properties[self.REQUIRES_MODULES]
        }
        return template

    def handle_create(self):
        '''Create the template on the BigIP.

        :raises: ResourceFailure
        '''

        template_dict = self.build_iapp_dict()
        self.get_bigip()

        try:
            self.bigip.iapp.create_template(
                name=self.properties[self.NAME],
                template=template_dict
            )
        except Exception as ex:
            raise exception.ResourceFailure(ex, None, action='CREATE')

    def handle_delete(self):
        '''Delete the iApp Template on the BigIP.

        :raises: ResourceFailure
        '''

        self.get_bigip()

        self.get_bigip()

        try:
            self.bigip.iapp.delete_template(
                self.properties[self.NAME]
            )
        except Exception as ex:
            raise exception.ResourceFailure(ex, None, action='DELETE')


def resource_mapping():
    return {'F5::Sys::iAppTemplate': F5SysiAppTemplate}
