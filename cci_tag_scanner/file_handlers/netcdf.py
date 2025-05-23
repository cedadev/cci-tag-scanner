# encoding: utf-8

__author__ = 'Daniel Westwood'
__date__ = '29 Oct 2024'
__copyright__ = 'Copyright 2024 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'daniel.westwood@stfc.ac.uk'

import netCDF4
import logging
import verboselogs

from .base import FileHandler
from cci_tag_scanner.conf.constants import PRODUCT_VERSION, ALLOWED_GLOBAL_ATTRS

verboselogs.install()
logger = logging.getLogger(__name__)

import logging
from cci_tag_scanner import logstream

logger = logging.getLogger(__name__)
logger.addHandler(logstream)
logger.propagate = False


class NetcdfHandler(FileHandler):

    def __init__(self, filepath):

        self.tags = {}
        self.nc_data = None
        self.filepath = filepath.as_posix()

        try:
            self.nc_data = netCDF4.Dataset(filepath)
        except Exception as e:
            logger.error(f'Read error. Could not open file: {filepath} with error: {e}')

    @staticmethod
    def is_level2(proc_level):
        """
        Convenience method to determine whether we are dealing with a level 2 product
        :param proc_level: processing level string
        :return: bool
        """
        return bool(proc_level is not None and '2' in proc_level)

    def get_product_version(self):
        """
        Get the product version from the file.
        We do not have a vocab for the product version so just extract value
        :return: attribute (string) | None
        """

        try:
            attr = self.nc_data.getncattr(PRODUCT_VERSION)
        except AttributeError:
            return

        return str(attr)

    def extract_facet_labels(self, proc_level):

        if self.nc_data:
            logger.debug(f'GLOBAL ATTRS for {self.filepath}')

            for global_attr in ALLOWED_GLOBAL_ATTRS:
                if global_attr in self.nc_data.ncattrs():
                    attr = self.nc_data.getncattr(global_attr)

                    self.tags[global_attr] = attr

                    # Verbose logging
                    logger.debug(f'{global_attr}={attr}')
                else:
                    logger.warning(f'Required attr {global_attr} not found in {self.filepath}')

            # Add product version
            product_version = self.get_product_version()

            if product_version:
                self.tags[PRODUCT_VERSION] = product_version

        return self.tags






