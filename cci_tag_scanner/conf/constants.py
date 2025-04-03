# encoding: utf-8

__author__ = 'Daniel Westwood'
__date__ = '29 Oct 2024'
__copyright__ = 'Copyright 2024 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'daniel.westwood@stfc.ac.uk'

# Values that are common across a number of modules
BROADER_PROCESSING_LEVEL = 'broader_processing_level'
DATA_TYPE = 'data_type'
ECV = 'ecv'
FREQUENCY = 'time_coverage_resolution'
INSTITUTION = 'institution'
PLATFORM = 'platform'
PLATFORM_PROGRAMME = 'platform_programme'
PLATFORM_GROUP = 'platform_group'
PROCESSING_LEVEL = 'processing_level'
PRODUCT_STRING = 'product_string'
PRODUCT_VERSION = 'product_version'
SENSOR = 'sensor'
PROJECT = 'project'

# Level 2 data is mapped to satellite orbit frequency
LEVEL_2_FREQUENCY = 'http://vocab.ceda.ac.uk/collection/cci/freq/freq_sat_orb'

# List of allowed netcdf attributes
ALLOWED_GLOBAL_ATTRS = [FREQUENCY, INSTITUTION, PLATFORM, SENSOR]
SINGLE_VALUE_FACETS = [BROADER_PROCESSING_LEVEL, DATA_TYPE, ECV, PROCESSING_LEVEL, PRODUCT_STRING, PROJECT]

DRS_FACETS = [ECV, FREQUENCY, PROCESSING_LEVEL, DATA_TYPE, SENSOR, PLATFORM, PRODUCT_STRING, PRODUCT_VERSION]
ALL_FACETS = [BROADER_PROCESSING_LEVEL, DATA_TYPE, ECV, FREQUENCY, INSTITUTION, PLATFORM, PLATFORM_PROGRAMME, PLATFORM_GROUP, PROCESSING_LEVEL, PRODUCT_STRING, PRODUCT_VERSION, SENSOR]

# Multilabels
MULTILABELS = {
    FREQUENCY: 'multi-frequency',
    INSTITUTION: 'multi-institution',
    PLATFORM: 'multi-platform',
    SENSOR: 'multi-sensor'
}

EXCLUDE_REALISATION = 'EXCLUDE'