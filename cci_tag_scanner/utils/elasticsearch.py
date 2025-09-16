# encoding: utf-8

__author__ = 'Daniel Westwood'
__date__   = '16 Sept 2025'
__copyright__ = 'Copyright 2025 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'daniel.westwood@stfc.ac.uk'

def es_connection_kwargs(hosts, api_key, **kwargs):
    """
    Determine Elasticsearch connection kwargs
    """
    if isinstance(hosts, list):
        hosts = hosts[0]

    if hosts == 'https://elasticsearch.ceda.ac.uk':
        return {
            'hosts': [hosts],
            'headers':{'x-api-key':api_key},
            **kwargs
        }
    else:
        return {
            'hosts':[hosts],
            'api_key':api_key,
            **kwargs
        }