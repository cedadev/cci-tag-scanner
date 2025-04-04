# encoding: utf-8

__author__ = 'Daniel Westwood'
__date__ = '29 Oct 2024'
__copyright__ = 'Copyright 2024 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'daniel.westwood@stfc.ac.uk'

from cci_tag_scanner.conf.constants import DATA_TYPE, FREQUENCY, INSTITUTION, PLATFORM, \
    SENSOR, ECV, PLATFORM_PROGRAMME, PLATFORM_GROUP, PROCESSING_LEVEL, \
    PRODUCT_STRING, BROADER_PROCESSING_LEVEL, PRODUCT_VERSION, PROJECT
from cci_tag_scanner.conf.settings import SPARQL_HOST_NAME

# Removal of the SPARQL Query/Triple Store components
#from cci_tag_scanner.triple_store import TripleStore, Concept

import re
import os
import requests
import json

import logging
from cci_tag_scanner import logstream
from typing import Union

logger = logging.getLogger(__name__)
logger.addHandler(logstream)
logger.propagate = False

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

class Facets(object):
    """
    This class is used to store data about the facets, that are obtained from
    the triple store.

    """

    # URL for the vocab server
    VOCAB_URL = f'http://{SPARQL_HOST_NAME}/scheme/cci'
    DEFAULT_ENDPOINT = f"http://{SPARQL_HOST_NAME}/ontology/cci/cci-content/cci-ontology.json"

    # All the desired facet endpoints
    FACET_ENDPOINTS = {
        DATA_TYPE: f'{VOCAB_URL}/dataType',
        ECV: f'{VOCAB_URL}/ecv',
        FREQUENCY: f'{VOCAB_URL}/freq',
        PLATFORM: f'{VOCAB_URL}/platform',
        PLATFORM_PROGRAMME: f'{VOCAB_URL}/platformProg',
        PLATFORM_GROUP: f'{VOCAB_URL}/platformGrp',
        PROCESSING_LEVEL: f'{VOCAB_URL}/procLev',
        SENSOR: f'{VOCAB_URL}/sensor',
        INSTITUTION: f'{VOCAB_URL}/org',
        PRODUCT_STRING: f'{VOCAB_URL}/product',
        PROJECT: f'{VOCAB_URL}/project'
    }

    LABEL_SOURCE = {
        BROADER_PROCESSING_LEVEL: '_get_pref_label',
        DATA_TYPE: '_get_alt_label',
        ECV: '_get_alt_label',
        FREQUENCY: '_get_pref_label',
        INSTITUTION: '_get_pref_label',
        PLATFORM: '_get_platform_label',
        PLATFORM_PROGRAMME: '_get_pref_label',
        PLATFORM_GROUP: '_get_pref_label',
        PROCESSING_LEVEL: '_get_alt_label',
        PRODUCT_STRING: '_get_pref_label',
        PRODUCT_VERSION: None,
        SENSOR: '_get_pref_label',
        PROJECT: '_get_pref_label'
    }

    def __init__(self, facet_dict: dict = None, endpoint: str = None, data: dict = None):

        facet_dict     = facet_dict or self.FACET_ENDPOINTS
        self._endpoint = endpoint or self.DEFAULT_ENDPOINT

        self._facet_dict = facet_dict
        self._reversed_facet_dict = dict((v,k) for k,v in facet_dict.items())

        self._broader  = {}
        self._narrower = {}
        self.__facets, self.__reversible_facets   = {},{}
        for f in self._facet_dict.keys():
            self.__facets[f] = {}
            self.__facets[f'{f}-alt'] = {}
            self.__reversible_facets[f] = {}
            self.__reversible_facets[f'{f}-alt'] = {}

        if data is not None:
            self._load_from_json(data)
            return

        # mapping from platform uri to platform programme label
        self.__platform_programme_mappings = {}

        # mapping from platform uri to platform group label
        self.__programme_group_mappings = {}

        # mapping for process levels
        self.__proc_level_mappings = {}

        # Perform decoding here
        if self._endpoint.startswith('http'):
            try:
                raw_content = requests.get(self._endpoint).json()
            except:
                raise ValueError(
                    f'Unable to retrieve JSON content from {self._endpoint}'
                )
        else:
            if os.path.isfile(self._endpoint):
                with open(self._endpoint) as f:
                    raw_content = json.load(f)
            else:
                raise IOError(
                    f'Specified endpoint - {self._endpoint} unreachable.'
                )
        
        self._decode_json(raw_content)
        self._reverse_facet_mappings()
        self._map_broad_narrow()

        bpl = {}
        for uri in set(self.__proc_level_mappings.values()):
            label = self.__reversible_facets[f'{PROCESSING_LEVEL}-alt'][uri]
            bpl[label] = uri
        self.__facets[BROADER_PROCESSING_LEVEL] = bpl

        self._reverse_facet_mappings(facet=BROADER_PROCESSING_LEVEL)

        self.__facets            = self._lower_all_facets(self.__facets)
        self.__reversible_facets = self._lower_all_facets(self.__reversible_facets, reverse=True)

        self.__facets = dict(sorted(self.__facets.items()))
        self.__reversible_facets = dict(sorted(self.__reversible_facets.items()))

        self.__programme_group_mappings = dict(sorted(self.__programme_group_mappings.items()))
        self.__proc_level_mappings = dict(sorted(self.__proc_level_mappings.items()))
        self.__platform_programme_mappings = dict(sorted(self.__platform_programme_mappings.items()))

    @property
    def facets(self) -> dict:
        return self.__facets
    
    @property
    def platform_programme_mappings(self) -> dict:
        return self.__platform_programme_mappings
    
    @property
    def programme_group_mappings(self) -> dict:
        return self.__programme_group_mappings
    
    @property
    def proc_level_mappings(self) -> dict:
        return self.__proc_level_mappings
    
    @property
    def reversed_facets(self) -> dict:
        return self.__reversible_facets
    
    def get_facet_names(self):
        """
        Get the list of facet names.

        @return  a list of str containing facet names

        """
        facet_names = []
        for key in self.__facets.keys():
            if not key.endswith('-alt'):
                facet_names.append(key)
        return facet_names

    def get_alt_labels(self, facet):
        """
        Get the facet alternative labels and URIs.

        @param facet (str): the name of the facet

        @return a dict where:\n
            key = lower case version of the concepts alternative label\n
            value = uri of the concept

        """
        return self.__facets[f'{facet}-alt']

    def get_labels(self, facet):
        """
        Get the facet labels and URIs.

        @param facet (str): the name of the facet

        @return a dict where:\n
            key = lower case version of the concepts preferred label\n
            value = uri of the concept

        """
        return self.__facets[facet]

    def get_platforms_programme(self, uri):
        """"
        Get the programme label for the given platform URI.

        @param uri (str): the URI of the platform

        @return a str containing the label of the programme that contains the
                platform

        """
        return self.__platform_programme_mappings.get(uri)

    def get_programme_labels(self):
        """
        Get a list of the programme labels, where a programme is a container
        for platforms.

        @return a list of str containing programme labels

        """
        return self.__platform_programme_mappings.values()

    def get_programmes_group(self, uri):
        """"
        Get the group label for the given programme URI.

        @param uri (str): the URI of the programme

        @return a str containing the label of the group that contains the
                programme

        """
        return self.__programme_group_mappings.get(uri)

    def get_group_labels(self):
        """
        Get a list of the group labels, where a group is a container
        for programmes.

        @return a list of str containing group labels

        """
        return self.__programme_group_mappings.values()

    def get_broader_proc_level(self, uri):
        """"
        Get the broader process level URI for the given process level URI.

        @param uri (str): the URI of the process level

        @return a str containing the label of the process level

        """
        return self.__proc_level_mappings.get(uri)

    def get_label_from_uri(self, facet, uri):
        """
        Mappings between facets and label getter
        BROADER_PROCESSING_LEVEL: pref,
        DATA_TYPE: alt,
        ECV: alt,
        FREQUENCY: pref,
        INSTITUTION: pref,
        PLATFORM: pref (made up of PLATFORM_PROGRAMME and PLATFORM_GROUP),
        PLATFORM_PROGRAMME: pref,
        PLATFORM_GROUP: pref,
        PROCESSING_LEVEL: alt,
        PRODUCT_STRING: pref,
        PRODUCT_VERSION: None,
        SENSOR: pref

        :param facet:
        :param uri:
        :return:
        """

        label_routing_string = self.LABEL_SOURCE.get(facet)

        if label_routing_string:

            # Turn string into a callable
            label_routing_func = getattr(self, label_routing_string)

            if label_routing_func:
                return label_routing_func(facet, uri)

        return uri

    def get_pref_label_from_alt_label(self, facet, label):
        """
        Reverse the lookup from alt label to pref label
        :param facet: facet label belongs to
        :param label: label to check
        :return: pref_label
        """

        facet_l = facet.lower()
        term_l = label.lower()

        # Check the term source
        mapping = self.LABEL_SOURCE.get(facet_l)

        if mapping:
            m = re.match(r'^_get_(?P<label>\w+)_label$', mapping)
            if m:
                source = m.group('label')

                # These sources are alread the pref label
                if source in ('pref', 'product'):
                    return term_l
                else:
                    # Get the URI and then get pref label
                    if term_l in self.get_alt_labels(facet):
                        uri = self.get_alt_labels(facet)[term_l].uri
                        return self._get_pref_label(facet_l, uri)
        return term_l

    def _get_pref_label(self, facet, uri):
        """
        Get the preferred label for the given facet and uri
        :param facet:
        :param uri:
        :return:
        """
        return self.__reversible_facets[facet].get(uri)

    def _get_alt_label(self, facet, uri):
        """
        Get the alt label for the given facet and uri
        :param facet:
        :param uri:
        :return:
        """
        return self.__reversible_facets[f'{facet}-alt'].get(uri)

    def _get_platform_label(self, facet, uri):
        """
        The platform uris are made up of three facets. Try each
        one to see if there is a match
        :param facet: unused
        :param uri:
        :return: label
        """

        for facet in [PLATFORM, PLATFORM_GROUP, PLATFORM_PROGRAMME]:
            label = self.__reversible_facets[facet].get(uri)

            if label:
                return label

        return uri

    def process_bag(self, bag):
        """
        Take a dictionary of facets with uris or strings and turn it into tags
        :param bag: dictionary of facets with lists of uris to convert
        :return: dictionary of facets with the extracted tags
        """
        output = {}

        for facet in bag:
            if isinstance(bag[facet],str):
                uri = bag[facet]

                # Filter out None values
                output[facet] = list(
                    filter(None, [self.get_label_from_uri(facet, uri)])
                )
            else:
                # Filter out None values
                output[facet] = list(
                    filter(None, [self.get_label_from_uri(facet, uri) for uri in bag[facet]])
                )

        return output

    def to_json(self, json_file: Union[str,None] = None) -> Union[dict,None]:
        """
        Write current generated outputs to a json file
        """
        response = {}

        # Get the __facet values
        __facet_dict = {}
        for facet, values in self.__facets.items():
            __facet_dict[facet] = {}
            for label, concept in values.items():
                # Concepts can either be a Concept Object or a string
                if isinstance(concept, str):
                    __facet_dict[facet][label] = concept
                else:
                    __facet_dict[facet][label] = concept.__dict__()

        response['__facets'] = __facet_dict

        # Add the other attributes
        response['__platform_programme_mappings'] = self.__platform_programme_mappings
        response['__programme_group_mappings'] = self.__programme_group_mappings
        response['__proc_level_mappings'] = self.__proc_level_mappings
        response['__reversible_facets'] = self.__reversible_facets

        if json_file is not None:
            with open(json_file,'w') as f:
                f.write(json.dumps(response))
            return None

        return response

    @classmethod
    def from_json(cls, json_file: Union[str,None] = None) -> object:
        """
        Generate the class instance from a json file.
        """
        if not os.path.isfile(json_file):
            raise FileNotFoundError(json_file)
        
        with open(json_file) as f:
            data = json.load(f)

        obj = cls(data=data)
        return obj
        
    def _load_from_json(self, data) -> None:
        """
        Extract values from a json file
        """
        __facet_dict = {}
        for facet, values in data['__facets'].items():
            __facet_dict[facet] = {}
            for label, concept in values.items():
                # Concepts can either be a Concept Object or a string
                if isinstance(concept, str):
                    __facet_dict[facet][label] = concept
                else:
                    __facet_dict[facet][label] = Concept(**concept)

        self.__facets = __facet_dict

        self.__platform_programme_mappings = data['__platform_programme_mappings']
        self.__programme_group_mappings = data['__programme_group_mappings']
        self.__proc_level_mappings = data['__proc_level_mappings']
        self.__reversible_facets = data['__reversible_facets']

    def _decode_json(self, raw_content: dict) -> None:
        """
        Decode the json schema passed from the ontology source
        """

        for record in raw_content:
            in_scheme = "http://www.w3.org/2004/02/skos/core#inScheme"

            id = record["@id"]

            if in_scheme not in record:
                # Record does not have an 'inScheme' option
                continue

            facet_label = record[in_scheme][0]["@id"]
            if facet_label not in self._facet_dict.values():
                # 'inScheme' ID does not conform to listed facets.
                continue

            facet_label = self._reversed_facet_dict[facet_label]

            prefLabel = "http://www.w3.org/2004/02/skos/core#prefLabel"
            altLabel  = "http://www.w3.org/2004/02/skos/core#altLabel"

            broader   = "http://www.w3.org/2004/02/skos/core#broader"
            narrower  = "http://www.w3.org/2004/02/skos/core#narrower"

            if broader in record:
                broad_id = record[broader][0]["@id"]
                self._broader[id] = (facet_label,broad_id)

            if narrower in record:
                for option in record[narrower]:
                    self._narrower[option["@id"]] = (id, facet_label)

            for option in record[prefLabel]:
                prefID = option["@value"]
                self.__facets[facet_label][prefID] = Concept(prefID, id)

            if altLabel not in record:
                # No alternative facet label.
                continue

            altID = record[altLabel][0]["@value"]
            self.__facets[f'{facet_label}-alt'][altID] = Concept(altID, id)

    def _reverse_facet_mappings(self, facet: Union[str,None] = None) -> None:
        """
        Reverse the facet mappings so that it can be given a uri and
        return the required tag.
        """

        if facet is None:
            iterable = self.__facets.items()
        else:
            iterable = [(facet, self.__facets[facet])]

        for facet, records in iterable:
            reversed = {}
            for k, v in records.items():
                if isinstance(v, str):
                    reversed[v] = k
                else:
                    reversed[v.uri] = v.tag

            self.__reversible_facets[facet] = reversed

    def _map_broad_narrow(self) -> None:
        """
        Map identified broad values to narrow ones.
        """

        processing_level = 'procLev'
        platform = 'platform'
        platform_prog = 'platformProg' 

        for id in self._broader.keys():

            (facet, mapping) = self._broader[id]

            if re.search(processing_level, id):
                self.__proc_level_mappings[id] = self._narrower[id][0]

            if re.search(platform_prog, id):
                facet_label = self._narrower[id][1]
                self.__programme_group_mappings[id] = self.__reversible_facets[facet_label][
                    mapping
                ]
            if re.search(platform, id):
                facet_label = self._narrower[id][1]
                self.__platform_programme_mappings[id] = self.__reversible_facets[facet_label][
                    mapping
                ]

    def _lower_all_facets(self, facets: dict, reverse: bool = False) -> dict:
        """
        Lower-case labels for all facet values."""
        new_facets = {}

        for facet, fset in facets.items():
            new_set = {}
            for label, lset in fset.items():
                if reverse:
                    new_set[label] = lset
                else:
                    new_set[label.lower()] = lset
            new_facets[facet] = new_set
        return new_facets
