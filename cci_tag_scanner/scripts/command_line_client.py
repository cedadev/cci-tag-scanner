
__author__ = 'Daniel Westwood'
__date__ = '29 Oct 2024'
__copyright__ = 'Copyright 2024 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'daniel.westwood@stfc.ac.uk'

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from datetime import datetime
import json
import sys
import time
import logging
import verboselogs
import os

from cci_tag_scanner.conf.settings import ERROR_FILE, LOG_FORMAT
from cci_tag_scanner.tagger import ProcessDatasets

verboselogs.install()
logger = logging.getLogger()

if not os.path.isfile(ERROR_FILE):
    os.system(f'touch {ERROR_FILE}')

# Set up ERROR file log handler
fh = logging.FileHandler(ERROR_FILE)
fh.setLevel(logging.ERROR)
LOG_FORMATTER = logging.Formatter(LOG_FORMAT)
fh.setFormatter(LOG_FORMATTER)

logger.addHandler(fh)

def get_logging_level(verbosity):

    map = {
        1: logging.INFO,
        2: verboselogs.VERBOSE,
        3: logging.DEBUG
    }

    if verbosity > max(map):
        verbosity = max(map)

    return map.get(verbosity,logging.ERROR)


def get_datasets_from_file(file_name):
    """
    Get a list of datasets from the given file.

    @param file_name (str): the name of the file containing the list of
            datasets to process

    @return a List(str) of datasets

    """
    datasets = set()
    with open(file_name) as reader:
        for ds in reader.readlines():
            datasets.add(ds.strip())

    return datasets


def read_json_file(file_name):
    """
    Get the contents from the given json file.

    @param file_name (str): the name of the json file

    @return the contents of the json file

    """

    with open(file_name) as json_data:
        data = json.load(json_data)

    return data


class CCITaggerCommandLineClient(object):

    @staticmethod
    def parse_command_line():
        parser = ArgumentParser(
            description='Tag observations. You can tag an individual dataset, '
            'or tag all the datasets'
            '\nlisted in a file.',
            epilog='\n\nA number of files are produced as output:'
            '\n  esgf_drs.json contains a list of DRS and associated files '
            'and check sums'
            '\n  moles_tags.csv contains a list of dataset paths and '
            'vocabulary URLs'
            '\n  error.txt contains a list of errors'
            '\n\nExamples:'
            '\n  moles_esgf_tag -d /neodc/esacci/cloud/data/L3C/avhrr_noaa-16 '
            '-v'
            '\n  moles_esgf_tag -f datapath --file_count 2 -v'
            '\n  moles_esgf_tag -j example.json -v'
            '\n  moles_esgf_tag -s',
            formatter_class=RawDescriptionHelpFormatter)

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '-d', '--dataset',
            help=('the full path to the dataset that is to be tagged. This '
                  'option is used to tag a single dataset.')
        )
        group.add_argument(
            '-f', '--file',
            help=('the name of the file containing a list of datasets to '
                  'process. This option is used for tagging one or more '
                  'datasets.')
        )
        group.add_argument(
            '-j', '--json_file',
            action='append',
            help=('Use the JSON file to provide a list of datasets and also provide the mappings'
                  'which are used by the tagging code. Useful to test datsets and specific mapping files')
        )

        parser.add_argument(
            '--file_count',
            help='how many .nc files to look at per dataset',
            type=int, default=0
        )

        parser.add_argument(
            '--ontology',
            help='Path to local ontology file',
            type=str, default=None
        )
        
        parser.add_argument(
            '-v', '--verbose', action='count',
            help='increase output verbosity',
            default=0
        )

        args = parser.parse_args()
        datasets = None

        start_time = time.strftime("%H:%M:%S")

        # Read datasets from the command line
        if args.dataset is not None:
            datasets = {args.dataset}

        # Read list of datasets from a file
        elif args.file is not None:
            datasets = get_datasets_from_file(args.file)

        # Given a json file, get the datasets from the datasets key
        elif args.json_file is not None:

            datasets = []
            for file in args.json_file:
                json_data = read_json_file(file)

                if json_data.get("datasets"):
                    datasets.extend(json_data["datasets"])

        # Print start time based on verbosity
        logger.info(f"{start_time} STARTED")
        if args.dataset:
            logger.info(f'Processing {args.dataset}')

        return datasets, args

    @classmethod
    def main(cls):

        start_time = datetime.now()

        # Get the command line arguments
        datasets, args = cls.parse_command_line()

        # Quit of there are no datasets
        if not datasets:
            logger.warning('You have not provided any datasets')
            sys.exit(0)

        if args.json_file:
            json_file = args.json_file
        else:
            json_file = None

        logger.info('Starting dataset process')
        pds = ProcessDatasets(json_files=json_file, ontology_local=args.ontology)
        pds.process_datasets(datasets, args.file_count)

        if logger.level <= logging.INFO:
            logger.info(f'{time.strftime("%H:%M:%S")} FINISHED\n\n')
            end_time = datetime.now()
            time_diff = end_time - start_time
            hours, remainder = divmod(time_diff.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            logger.info(f'Time taken {hours:02d}:{minutes:02d}:{seconds:02d}')

        exit(0)


if __name__ == "__main__":
    CCITaggerCommandLineClient.main()
