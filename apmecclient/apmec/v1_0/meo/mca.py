# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICEMCAE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIOMCA OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import yaml

from apmecclient.common import exceptions
from apmecclient.i18n import _
from apmecclient.apmec import v1_0 as apmecV10


_MCA = 'mca'
_RESOURCE = 'resource'


class ListMCA(apmecV10.ListCommand):
    """List MCA that belong to a given tenant."""

    resource = _MCA
    list_columns = ['id', 'name', 'mcad_id', 'mgmt_urls', 'status']


class ShowMCA(apmecV10.ShowCommand):
    """Show information of a given MCA."""

    resource = _MCA


class CreateMCA(apmecV10.CreateCommand):
    """Create a MCA."""

    resource = _MCA
    remove_output_fields = ["attributes"]

    def add_known_arguments(self, parser):
        parser.add_argument(
            'name', metavar='NAME',
            help=_('Set a name for the MCA'))
        parser.add_argument(
            '--description',
            help=_('Set description for the MCA'))
        mcad_group = parser.add_mutually_exclusive_group(required=True)
        mcad_group.add_argument(
            '--mcad-id',
            help=_('MCAD ID to use as template to create MCA'))
        mcad_group.add_argument(
            '--mcad-template',
            help=_('MCAD file to create MCA'))
        mcad_group.add_argument(
            '--mcad-name',
            help=_('MCAD name to use as template to create MCA'))
        vim_group = parser.add_mutually_exclusive_group()
        vim_group.add_argument(
            '--vim-id',
            help=_('VIM ID to use to create MCA on the specified VIM'))
        vim_group.add_argument(
            '--vim-name',
            help=_('VIM name to use to create MCA on the specified VIM'))
        parser.add_argument(
            '--vim-region-name',
            help=_('VIM Region to use to create MCA on the specified VIM'))
        parser.add_argument(
            '--param-file',
            help=_('Specify parameter yaml file'))

    def args2body(self, parsed_args):
        args = {'attributes': {}}
        body = {self.resource: args}
        if parsed_args.vim_region_name:
            args.setdefault('placement_attr', {})['region_name'] = \
                parsed_args.vim_region_name

        apmec_client = self.get_client()
        apmec_client.format = parsed_args.request_format
        if parsed_args.vim_name:
                _id = apmecV10.find_resourceid_by_name_or_id(apmec_client,
                                                              'vim',
                                                              parsed_args.
                                                              vim_name)
                parsed_args.vim_id = _id
        if parsed_args.mcad_name:
                _id = apmecV10.find_resourceid_by_name_or_id(apmec_client,
                                                              'mcad',
                                                              parsed_args.
                                                              mcad_name)
                parsed_args.mcad_id = _id
        elif parsed_args.mcad_template:
            with open(parsed_args.mcad_template) as f:
                template = f.read()
            try:
                args['mcad_template'] = yaml.load(
                    template, Loader=yaml.SafeLoader)
            except yaml.YAMLError as e:
                raise exceptions.InvalidInput(e)
            if not args['mcad_template']:
                raise exceptions.InvalidInput('The mcad file is empty')

        if parsed_args.param_file:
            with open(parsed_args.param_file) as f:
                param_yaml = f.read()
            try:
                args['attributes']['param_values'] = yaml.load(
                    param_yaml, Loader=yaml.SafeLoader)
            except yaml.YAMLError as e:
                raise exceptions.InvalidInput(e)
        apmecV10.update_dict(parsed_args, body[self.resource],
                              ['tenant_id', 'name', 'description',
                               'mcad_id', 'vim_id'])
        return body


class DeleteMCA(apmecV10.DeleteCommand):
    """Delete given MCA(s)."""

    resource = _MCA
    deleted_msg = {'mca': 'delete initiated'}
