# encoding: utf-8

__author__ = 'Daniel Westwood'
__date__ = '29 Oct 2024'
__copyright__ = 'Copyright 2024 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'daniel.westwood@stfc.ac.uk'

from rdflib import Dataset, Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from six import with_metaclass
from builtins import str

from tag_scanner.conf.settings import SPARQL_HOST_NAME


class Concept:
    """
    Storage object for concepts to allow
    the terms to be reveresed and get the
    correct tag in return.
    """

    def __init__(self, tag, uri):
        self.uri = str(uri)
        self.tag = str(tag)

    def __repr__(self):
        return self.uri

    def __dict__(self):
        return {
            'uri': self.uri,
            'tag': self.tag
        }


class TripleStoreMC(type):
    """
    This class provides methods to query the triple store.

    """

    # an instance of a ConjunctiveGraph
    __graph = None

    # This allows us to use the prefix values in the queries rather than the
    # url
    __prefix = """
    PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX skos:  <http://www.w3.org/2004/02/skos/core#>
    """

    # Cache the pref and alt labels
    __alt_label_cache = {}
    __pref_label_cache = {}

    @property
    def _graph(self):
        """
        Get the graph, creating a new one if necessary.

        """

        if self.__graph is None:
            store = SPARQLStore(
                query_endpoint='http://%s/sparql' % (SPARQL_HOST_NAME))
            self.__graph = Dataset(store=store)
        return self.__graph

    @classmethod
    def get_concepts_in_scheme(cls, uri):
        """
        Get the preferred labels of all of the concepts for the given concept
        scheme.

        @param uri (str): the uri of the concept scheme

        @return a dict where:\n
                key = lower case version of the concepts preferred label\n
                value = uri of the concept

        """
        graph = TripleStore._graph
        statement = ('%s SELECT ?concept ?label WHERE { GRAPH ?g {?concept '
                     'skos:inScheme <%s> . ?concept skos:prefLabel ?label} }' %
                     (cls.__prefix, uri))
        result_set = graph.query(statement)

        concepts = {}
        for result in result_set:
            concepts[("" + result.label).lower()] = Concept(result.label, result.concept.toPython())

        return concepts

    @classmethod
    def get_nerc_concepts_in_scheme(cls, uri):
        """
        Get the preferred labels of all of the concepts for the given concept
        scheme where the actual concepts are hosted by NERC.

        @param uri (str): the uri of the concept scheme

        @return a dict where:\n
                key = lower case version of the concepts alternative label\n
                value = uri of the concept

        """
        graph = TripleStore._graph
        statement = (
                '%s SELECT ?concept WHERE { GRAPH ?g {?concept skos:inScheme <%s> '
                'FILTER regex(str(?concept), "^http://vocab.nerc.ac.uk", "i")}}' %
                (cls.__prefix, uri))
        result_set = graph.query(statement)
        concepts = {}

        for result in result_set:
            uri = result.concept.toPython()
            label = cls._get_nerc_pref_label(uri).lower()
            concepts[label] = Concept(label, uri)

        return concepts

    @classmethod
    def get_alt_concepts_in_scheme(cls, uri):
        """
        Get the alternative labels of all of the concepts for the given concept
        scheme.

        @param uri (str): the uri of the concept scheme

        @return a dict where:\n
                key = lower case version of the concepts alternative label\n
                value = uri of the concept

        """
        graph = TripleStore._graph
        statement = ('%s SELECT ?concept ?label WHERE { GRAPH ?g {?concept '
                     'skos:inScheme <%s> . ?concept skos:altLabel ?label} }' %
                     (cls.__prefix, uri))
        result_set = graph.query(statement)

        concepts = {}
        for result in result_set:
            concepts[("" + result.label).lower()] = Concept(result.label, result.concept.toPython())

        return concepts

    @classmethod
    def get_nerc_alt_concepts_in_scheme(cls, uri):
        """
        Get the alternative labels of all of the concepts for the given concept
        scheme where the actual concepts are hosted by NERC.

        @param uri (str): the uri of the concept scheme

        @return a dict where:\n
                key = lower case version of the concepts alternative label\n
                value = uri of the concept

        """
        graph = TripleStore._graph
        statement = (
                '%s SELECT ?concept WHERE { GRAPH ?g {?concept skos:inScheme <%s> '
                'FILTER regex(str(?concept), "^http://vocab.nerc.ac.uk", "i")}}' %
                (cls.__prefix, uri))
        result_set = graph.query(statement)

        concepts = {}
        for result in result_set:
            uri = result.concept.toPython()
            label = cls._get_nerc_pref_label(uri).lower()
            concepts[label] = Concept(label, uri)

        return concepts

    @classmethod
    def get_pref_label(cls, uri):
        """
        Get the preferred label for the concept with the given uri.

        @param uri (str): the uri of the concept

        @return a str containing the preferred label

        """
        # Check for none value of uri
        if uri is None:
            return ''

        # check for cached value
        if cls.__pref_label_cache.get(uri) is not None:
            return cls.__pref_label_cache.get(uri)

        if 'vocab.nerc' in uri:
            return cls._get_nerc_pref_label(uri)
        else:
            return cls._get_ceda_pref_label(uri)

    @classmethod
    def _get_ceda_pref_label(cls, uri):
        graph = TripleStore._graph
        statement = ('%s SELECT ?label WHERE { GRAPH ?g {<%s> skos:prefLabel '
                     '?label} }' % (cls.__prefix, uri))
        results = graph.query(statement)

        # there should only be one result
        for resource in results:
            cls.__pref_label_cache[uri] = resource.label.toPython()
            return resource.label.toPython()

        cls.__pref_label_cache[uri] = ''
        return ''

    @classmethod
    def _get_nerc_pref_label(cls, uri):
        graph = Graph()
        graph.parse(location=uri, format='application/rdf+xml')
        statement = ('%s SELECT ?label WHERE {<%s> skos:altLabel ?label}' %
                     (cls.__prefix, uri))
        results = graph.query(statement)

        # there should only be one result
        for resource in results:
            label = resource.label.strip().replace(u'\xa0', u' ').toPython()
            cls.__pref_label_cache[uri] = label
            return label

        cls.__pref_label_cache[uri] = ''
        return ''

    @classmethod
    def get_alt_label(cls, uri):
        """
        Get the alternative label for the concept with the given uri.

        @param uri (str): the uri of the concept

        @return a str containing the alternative label

        """
        # Check for none value of uri
        if uri is None:
            return ''

        # check for cached value
        if cls.__alt_label_cache.get(uri) is not None:
            return cls.__alt_label_cache.get(uri)

        if 'vocab.nerc' in uri:
            return cls._get_nerc_alt_label(uri)
        else:
            return cls._get_ceda_alt_label(uri)

    @classmethod
    def _get_ceda_alt_label(cls, uri):
        graph = TripleStore._graph
        statement = ('%s SELECT ?label WHERE { GRAPH ?g {<%s> skos:altLabel '
                     '?label} }' % (cls.__prefix, uri))
        results = graph.query(statement)

        # there should only be one result
        for resource in results:
            cls.__alt_label_cache[uri] = resource.label.toPython()
            return resource.label.toPython()

        cls.__alt_label_cache[uri] = ''
        return ''

    @classmethod
    def _get_nerc_alt_label(cls, uri):
        graph = Graph()
        graph.parse(location=uri, format='application/rdf+xml')
        statement = ('%s SELECT ?label WHERE {<%s> skos:prefLabel ?label}' %
                     (cls.__prefix, uri))
        results = graph.query(statement)

        # there should only be one result
        for resource in results:
            label = resource.label.strip().replace(u'\xa0', u' ').toPython()
            cls.__alt_label_cache[uri] = label
            return label

        cls.__alt_label_cache[uri] = ''
        return ''

    @classmethod
    def get_broader(cls, uri):
        """
        Get the broader concept for the concept with the given uri.

        @param uri (str): the uri of the concept

        @return a tuple where:\n
                [0] = lower case version of the concepts preferred label\n
                [1] = uri of the concept

        """
        graph = TripleStore._graph
        statement = ('%s SELECT ?concept ?label WHERE { GRAPH ?g {?concept '
                     'skos:narrower <%s> . ?concept skos:prefLabel ?label} }' %
                     (cls.__prefix, uri))
        results = graph.query(statement)

        # there should only be one result
        for resource in results:
            return (resource.label.toPython(), resource.concept.toPython())
        return '', ''


class TripleStore(with_metaclass(TripleStoreMC)):
    pass
