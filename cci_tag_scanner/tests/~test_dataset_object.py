# encoding: utf-8

__author__ = 'Daniel Westwood'
__date__ = '29 Oct 2024'
__copyright__ = 'Copyright 2024 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'daniel.westwood@stfc.ac.uk'

import glob

from cci_tag_scanner.utils.dataset_jsons import DatasetJSONMappings
from cci_tag_scanner.dataset.dataset import Dataset
from cci_tag_scanner.facets import Facets


PATH = 'permafrost/*'
JSON_TAGGER_ROOT = 'test_json_files/'

class TestDatasetObject:
    def test_mappings(self, json_tagger_root=JSON_TAGGER_ROOT):
        """
        Test mappings
        """
        mappings = DatasetJSONMappings(json_tagger_root=json_tagger_root)
        facets   = Facets()

        for path in glob.glob(PATH)[:1]:

            dataset_id = mappings.get_dataset(path)

            dataset = Dataset(dataset_id, mappings, facets)

            uris = dataset.get_file_tags(filepath=path)

            tags = facets.process_bag(uris)

            drs_facets = dataset.get_drs_labels(tags)

            drs = dataset.generate_ds_id(drs_facets, path)

            print(uris)

            print(tags)

            print(drs_facets)

            print(drs)

if __name__ == '__main__':
    TestDatasetObject().test_mappings()