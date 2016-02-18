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

from common.mixins import f5_common_resources
from common.mixins import F5BigIPMixin
from f5.common.iapp_parser import IappParser


class IappTemplateStackValidationFailed(exception.StackValidationFailed):
    pass


class F5SysiAppTemplate(F5BigIPMixin, resource.Resource):
    '''Manages creation of an iApp resource on the BigIP device.'''

    PROPERTIES = (
        NAME,
        BIGIP_SERVER,
        PARTITION,
        COMPOSITE_TEMPLATE,
        FULL_TEMPLATE
    ) = (
        'name',
        'bigip_server',
        'partition',
        'composite_template',
        'full_template'
    )

    _COMPOSITE_TEMPLATE_PROPERITES = (
        REQUIRES_MODULES,
        IMPLEMENTATION,
        PRESENTATION,
        HELP,
        ROLE_ACL
    ) = (
        'requires_modules',
        'implementation',
        'presentation',
        'help',
        'role-acl'
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
        PARTITION: properties.Schema(
            properties.Schema.STRING,
            _('Partition resource reference.'),
            required=True
        ),
        COMPOSITE_TEMPLATE: properties.Schema(
            properties.Schema.MAP,
            _('Parts of the template to create. The necessary minimum is: '
              'implementation and presentation.'),
            required=False,
            schema={
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
                    _('Help section of the template.')
                ),
                ROLE_ACL: properties.Schema(
                    properties.Schema.LIST,
                    _('Access control list roles as string.')
                )
            }
        ),
        FULL_TEMPLATE: properties.Schema(
            properties.Schema.STRING,
            _('Full iapp template string.')
        )
    }

    def __init__(self, name, definition, stack):
        super(F5SysiAppTemplate, self).__init__(name, definition, stack)
        if self.properties[self.FULL_TEMPLATE]:
            if self.properties[self.COMPOSITE_TEMPLATE]:
                message = _('Full template and composite template cannot both '
                            'be defined in an F5::Sys::iAppTemplate resource.')
                raise IappTemplateStackValidationFailed(message)

    def _add_optional_attr(self, iapp_dict):
        '''When building the iapp dictionary, add optional items.

        :param iapp_dict: dictionary for iapp template
        :returns: possibly modified dictionary
        '''

        if self.properties[self.COMPOSITE_TEMPLATE][self.REQUIRES_MODULES]:
            iapp_dict['requiresModules'] = \
                self.properties[self.COMPOSITE_TEMPLATE][self.REQUIRES_MODULES]

        if self.properties[self.COMPOSITE_TEMPLATE][self.ROLE_ACL]:
            iapp_dict['actions']['definition']['roleAcl'] = \
                self.properties[self.COMPOSITE_TEMPLATE][self.ROLE_ACL]

        return iapp_dict

    def _build_iapp_dict(self):
        '''Build dictionary for posting to BigIP.

        :returns: dictionary of template information
        '''

        sections = {
            'implementation': self.properties[
                self.COMPOSITE_TEMPLATE][self.IMPLEMENTATION] or '',
            'presentation': self.properties[
                self.COMPOSITE_TEMPLATE][self.PRESENTATION] or ''
        }
        definition = {'definition': sections}
        template = {
            'name': self.properties[self.NAME],
            'actions': definition,
        }

        return self._add_optional_attr(template)

    @f5_common_resources
    def handle_create(self):
        '''Create the template on the BigIP.

        :raises: ResourceFailure
        '''

        template_dict = {}
        if self.properties[self.COMPOSITE_TEMPLATE]:
            template_dict = self._build_iapp_dict()
            template_dict['partition'] = self.partition_name
        else:
            parser = IappParser(self.properties[self.FULL_TEMPLATE])
            template_dict = parser.parse_template()

        try:
            template = self.bigip.sys.applications.templates.template
            template.create(**template_dict)
        except Exception as ex:
            raise exception.ResourceFailure(ex, None, action='CREATE')

    @f5_common_resources
    def handle_delete(self):
        '''Delete the iApp Template on the BigIP.

        :raises: ResourceFailure
        '''

        try:
            loaded_template = self.bigip.sys.applications.templates.template.\
                load(
                    name=self.properties[self.NAME],
                    partition=self.partition_name
                )
            loaded_template.delete()
        except Exception as ex:
            raise exception.ResourceFailure(ex, None, action='DELETE')


def resource_mapping():
    return {'F5::Sys::iAppTemplate': F5SysiAppTemplate}
