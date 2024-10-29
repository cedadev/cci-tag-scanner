# encoding: utf-8

__author__ = 'Daniel Westwood'
__date__ = '29 Oct 2024'
__copyright__ = 'Copyright 2024 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'daniel.westwood@stfc.ac.uk'

from tag_scanner.utils.dataset_jsons import DatasetJSONMappings
from tag_scanner.dataset.dataset import Dataset
from tag_scanner.facets import Facets


PATH = 'biomass/ESACCI-BIOMASS-L4-AGB-MERGED-100m-2017-fv1.0.nc'
JSON_TAGGER_ROOT = ''

class TestDatasetObject:
    def test_mappings(self, json_tagger_root=JSON_TAGGER_ROOT):
        """
        Test mappings
        """
        mappings = DatasetJSONMappings(json_tagger_root=json_tagger_root)
        facets   = Facets()

        dataset_id = mappings.get_dataset(PATH)

        dataset = Dataset(dataset_id, mappings, facets)

        uris = dataset.get_file_tags(filepath=PATH)

        tags = facets.process_bag(uris)

        drs_facets = dataset.get_drs_labels(tags)

        drs = dataset.generate_ds_id(drs_facets, PATH)

        print(uris)

        print(tags)

        print(drs_facets)

        print(drs)

