# encoding: utf-8
__author__ = 'Daniel Westwood'
__date__ = '29 Oct 2024'
__copyright__ = 'Copyright 2024 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'daniel.westwood@stfc.ac.uk'

import argparse
import json

from cci_tag_scanner.facets import Facets


def get_args():
    parser = argparse.ArgumentParser('Dump facet object for use by lotus')
    parser.add_argument('output', help='Output file')
    return parser.parse_args()


def main():
    args = get_args()
    facets = Facets()

    with open(args.output, 'w') as writer:
        json.dump(facets.to_json(), writer)


if __name__ == '__main__':
    main()
