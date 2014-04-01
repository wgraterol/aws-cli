# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import logging

from awscli.customizations.flatten import FlattenArguments, SEP
from botocore.compat import OrderedDict

LOG = logging.getLogger(__name__)

DEFAULT_VALUE_TYPE_MAP = {
    'Int': int,
    'Double': float,
    'IntArray': int,
    'DoubleArray': float
}


def index_hydrate(params, container, cli_type, key, value):
    """
    Hydrate an index-field option value to construct something like::

        {
            'index_field': {
                'DoubleOptions': {
                    'DefaultValue': 0.0
                }
            }
        }
    """
    if 'index_field' not in params:
        params['index_field'] = {}

    if 'IndexFieldType' not in params['index_field']:
        raise RuntimeError('You must pass the --type option!')

    # Find the type and transform it for the type options field name
    # E.g: int-array => IntArray
    _type = params['index_field']['IndexFieldType']
    _type = ''.join([i.capitalize() for i in _type.split('-')])

    # Transform string value to the correct type?
    if key.split(SEP)[-1] == 'DefaultValue':
        value = DEFAULT_VALUE_TYPE_MAP.get(_type, lambda x: x)(value)

    # Set the proper options field
    if _type + 'Options' not in params['index_field']:
        params['index_field'][_type + 'Options'] = {}

    params['index_field'][_type + 'Options'][key.split(SEP)[-1]] = value


FLATTEN_CONFIG = {
    "define-expression": {
        "expression": {
            "keep": False,
            "flatten": {
                "ExpressionName": {
                    "name": "name"
                },
                "ExpressionValue": {
                    "name": "expression"
                }
            }
        }
    },
    "define-index-field": {
        "index-field": {
            "keep": False,
            # We use an ordered dict because `type` needs to be parsed before
            # any of the <X>Options values.
            "flatten": OrderedDict([
                ("IndexFieldName", {
                    "name": "name"
                }),
                ("IndexFieldType", {
                    "name": "type"
                }),
                ("IntOptions.DefaultValue", {
                    "name": "default-value",
                    "type": "string",
                    "hydrate": index_hydrate
                }),
                ("IntOptions.FacetEnabled", {
                    "name": "facet-enabled",
                    "hydrate": index_hydrate
                }),
                ("IntOptions.SearchEnabled", {
                    "name": "search-enabled",
                    "hydrate": index_hydrate
                }),
                ("IntOptions.ReturnEnabled", {
                    "name": "return-enabled",
                    "hydrate": index_hydrate
                }),
                ("IntOptions.SortEnabled", {
                    "name": "sort-enabled",
                    "hydrate": index_hydrate
                }),
                ("TextOptions.HighlightEnabled", {
                    "name": "highlight-enabled",
                    "hydrate": index_hydrate
                }),
                ("TextOptions.AnalysisScheme", {
                    "name": "analysis-scheme",
                    "hydrate": index_hydrate
                })
            ])
        }
    }
}


def initialize(cli):
    """
    The entry point for CloudSearch customizations.
    """
    flattened = FlattenArguments('cloudsearch', FLATTEN_CONFIG)
    flattened.register(cli)
