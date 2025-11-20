# encoding: utf-8

__author__ = 'Daniel Westwood'
__date__   = '16 Sept 2025'
__copyright__ = 'Copyright 2025 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'daniel.westwood@stfc.ac.uk'

from elasticsearch import Elasticsearch

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
    
class ElasticsearchConnection:
    """
    Elasticsearch Connection class.

    :param index: files index (default: settings.ELASTICSEARCH_INDEX)
    :type index: str

    """

    def __init__(self, host, api_key, index=None, collection_index=None, connection_params=None):
        self.index = index
        self.collection_index = collection_index

        connection_params = connection_params or {}

        if isinstance(api_key,str):
            api_key = api_key.rstrip()

        self.es = Elasticsearch(
            **es_connection_kwargs(
                hosts=[host],
                api_key=api_key,
                **connection_params
            )
        )

    def get(self, *args, **kwargs):
        """Get Query"""
        return self.es.get(*args, **kwargs)

    def search(self, query):
        """
        Search the files index

        :param query: Elasticsearch file query
        :type query: dict

        :return: Elasticsearch response
        :rtype: dict
        """
        try:
            return self.es.search(index=self.index, body=query)
        except:
            print(None)
            raise ValueError()

    def search_collections(self, query):
        """
        Search the collections index

        :param query: Elasticsearch collection query
        :type query: dict

        :return: Elasticsearch response
        :rtype: dict
        """
        return self.es.search(index=self.collection_index, body=query)

    def count(self, query):
        """
        Return the hit count from the current file query

        :param query: Elasticsearch file query
        :type query: dict

        :return: Elasticsearch count response
        :rtype: dict
        """
        return self.es.count(index=self.index, body=query)

    def count_collections(self, query):
        """
        Return the hit count from the current collection query

        :param query: Elasticsearch collection query
        :type query: dict

        :return: Elasticsearch count response
        :rtype: dict
        """
        return self.es.count(index=self.collection_index, body=query)