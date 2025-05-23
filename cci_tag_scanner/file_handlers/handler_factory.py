# encoding: utf-8

__author__ = 'Daniel Westwood'
__date__ = '29 Oct 2024'
__copyright__ = 'Copyright 2024 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'daniel.westwood@stfc.ac.uk'

from pydoc import locate


class HandlerFactory(object):

    HANDLER_MAP = {
        '.nc': 'cci_tag_scanner.file_handlers.netcdf.NetcdfHandler'
    }

    @classmethod
    def get_handler(cls, extension):

        handler = cls.HANDLER_MAP.get(extension)

        if handler:
            return locate(handler)