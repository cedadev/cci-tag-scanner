# encoding: utf-8
"""
"""
__author__ = 'Richard Smith'
__date__ = '27 Jan 2020'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from ceda_directory_tree import DatasetNode
import os
import json
from pathlib import Path
import re
import glob

import logging

from cci_tag_scanner import logstream

logger = logging.getLogger(__name__)
logger.addHandler(logstream)
logger.propagate = False

def nested_get(key_list, input_dict):
    """
    Takes an iterable of keys and returns none if not found or the value
    :param key_list:
    :return:

    """

    last_key = key_list[-1]
    dict_nest = input_dict

    for key in key_list:
        if key != last_key:
            dict_nest = dict_nest.get(key, {})
        else:
            return dict_nest.get(key)

class DatasetJSONMappings:

    def __init__(self, json_files=None, json_tagger_root=None):
        """
        :param json_files: A collection of json files to read in.

        """

        # A mapping between the datasets and the filepath to the JSON file
        # containing the mappings
        self._json_lookup = {}
        self._partial_jsons = {}

        # Place to cache the loaded mappings from the JSON files once they are required
        # in the processing
        self._user_json_cache = {}

        # Init tree
        self._dataset_tree = DatasetNode()

        if not json_files:
            logger.warning('No JSON files provided, will look for JSON_TAGGER_ROOT environment var')

            if not json_tagger_root:
                json_tagger_root = os.environ.get('JSON_TAGGER_ROOT')

            if not json_tagger_root:
                logger.error(
                    'No JSON files could be identfied for use when tagging. '
                    'Please provide a file or path to the set of JSON files.'
                )
                json_files = []

            else:

                path_root = os.path.abspath(json_tagger_root)
                # Must use recursive to final all files
                json_files = glob.glob(f'{path_root}/**/*.json', recursive=True)

        # Read all the json files and build a tree of datasets
        i = 0
        for f in json_files:

            with open(f) as json_input:
                try:
                    data = json.load(json_input)
                except json.decoder.JSONDecodeError as e:
                    print(f'Error loading {f}: {e}')
                    continue

            for dataset in data.get('datasets',[]):

                # Strip trailing slash. Needed to make sure tree search works
                dataset = dataset.rstrip('/')

                self._dataset_tree.add_child(dataset)
                if 'partial' in f:
                    self._partial_jsons[dataset] = f
                else:
                    self._json_lookup[dataset] = f
            i += 1

        j = 0
        # Recombine partials if needed
        for dataset, pfile in self._partial_jsons.items():
            if dataset not in self._json_lookup:
                self._json_lookup[dataset] = pfile
                j += 1

        logger.info(f'Loading JSONs from {json_tagger_root}')
        logger.info(f'Loaded {i} JSON files')
        logger.info(f'Loaded {j} partial JSON files')

    def get_dataset(self, path):
        """
        Returns the dataset which directly matches the given file path
        :param path: Filepath to match (String)
        :return: Dataset (string) | default: None
        """

        ds = self._dataset_tree.search_name(path)

        if ds:
            return ds[:-1]

        return path

    def get_user_defined_mapping(self, dataset):
        """
        Load the relevant JSON file and return the "mappings" section.
        Will return {} if no mapping found.
        :return: mappings (dict) | {}
        """

        data = self.load_mapping(dataset)

        return data.get('mappings', {})

    def load_mapping(self, dataset):
        """
        Handles lazy loading of the file
        :param dataset:
        :return: json_data (Dict)
        """
        json_data = {}

        # Look up the mapping file
        mapping_file = self._json_lookup.get(dataset)

        if mapping_file:
            logger.info(f'Identified mapping file: {mapping_file}')

            json_data = self._user_json_cache.get(dataset)

            # If the file hasn't been loaded yet, read the contents of the file
            # and store
            if json_data is None:

                with open(mapping_file) as reader:
                    json_data = json.load(reader)
                    self._user_json_cache[dataset] = json_data

        return json_data

    def get_user_defined_defaults(self, dataset):
        """
        Load the relevant JSON file and return the "defaults" section.
        Will return {} if no defaults found.
        :param dataset: (string)
        :return: defaults (dict) | {}
        """

        data = self.load_mapping(dataset)

        return data.get('defaults', {})

    def get_merged_attribute(self, dataset, attr):
        """
        In some cases, the attribute from the file is a merged list of many attributes.
        This method maps a complex string to a simpler comma separated string
        which can be used in the next steps of the code.
        :param dataset: Dataset we are working with
        :param attr: The attribute to map
        :return: The mapped term or original string if no map found
        """

        # Load the mapping
        mappings = self.get_user_defined_mapping(dataset)

        merged = mappings.get('merged')

        # Check if there is a merged attribute in the mapping
        if merged:
            mapped_val = merged.get(attr)

            # Return the mapped value, if there is one
            if mapped_val:
                return mapped_val

        # Defaults to returning the input attribute
        return attr

    def get_user_defined_overrides(self, dataset):
        """
        Load the relevant JSON file and return the overrides section.
        Will return None if no overrides found.
        :param dataset: (string)
        :return: overrides (dict) | None
        """

        data = self.load_mapping(dataset)

        return data.get('overrides')

    def get_dataset_realisation(self, dataset, filepath):
        """
        Get the realisation for the specified dataset.
        Returns 'r1' if no user defined realisations.
        The filepath is used to match against a filter, if there is one.

        Order:
         - Default realisation 'r1'
         - Checks to see if there a dataset specific realisation
         - Checks to see if there is a filter to hone the realisation

        :param dataset: (string)
        :param filepath: (string)
        :return: realisation (string) | 'r1'
        """

        # Set default
        realisation = 'r1'

        # Load the relevant json file
        data = self.load_mapping(dataset)

        # Check for dataset level realisation mappings
        keys = ('realisations',dataset)
        if nested_get(keys, data):
            realisation = nested_get(keys, data)

        # Check for dataset realisations for dataset with trailing slash
        keys = ('realisations', f'{dataset}/')
        if nested_get(keys, data):
            realisation = nested_get(keys, data)

        # Check if there are filters for dataset
        keys = ('filters', dataset)
        filters = nested_get(keys, data)

        # Check if there are filters for dataset with trailing slash
        if not filters:
            keys = ('filters', f'{dataset}/')
            filters = nested_get(keys, data)

        # If there are filters, these override dataset level realisations
        if filters:

            # Check file against all filters
            for filter in filters:
                m = re.match(filter['pattern'],str(filepath))

                if m:
                    ds_real = filter.get('realisation')
                    if ds_real:
                        realisation = ds_real
                    break

        return realisation

    def get_aggregations(self, filepath):

        # Get dataset
        dataset = self.get_dataset(filepath)

        # Load the relevant json file
        data = self.load_mapping(dataset)

        return data.get('aggregations')

if __name__ == '__main__':

    files = ['/neodc/esacci/sea_surface_salinity/data/v01.8/30days/2013/ESACCI-SEASURFACESALINITY-L4-SSS-MERGED_OI_Monthly_CENTRED_15Day_25km-20130101-fv1.8.nc',
             '/neodc/esacci/sea_surface_salinity/data/v01.8/7days/2014/ ESACCI-SEASURFACESALINITY-L4-SSS-MERGED_OI_7DAY_RUNNINGMEAN_DAILY_25km-20140101-fv1.8.nc']

    tree = DatasetJSONMappings(None)

    for f in files:
        print("Dataset")
        ds = tree.get_dataset(f)
        print(ds)
        print()

        print("Mapping")
        print(tree.get_user_defined_mapping(ds))
        print()

        print("Defaults")
        print(tree.get_user_defined_defaults(ds))
        print()

        print("Overrides")
        print(tree.get_user_defined_overrides(ds))
        print()

        print("Realisation")
        print(tree.get_user_defined_overrides(ds))
        print()

        print(tree._json_lookup)