class TestConsistency:
    def test_dataset(self):
        from cci_tag_scanner.dataset import Dataset

    def test_file_handlers(self):
        from cci_tag_scanner.file_handlers.base import FileHandler
        from cci_tag_scanner.file_handlers.handler_factory import HandlerFactory
        from cci_tag_scanner.file_handlers.netcdf import NetcdfHandler

    def test_scripts(self):
        from cci_tag_scanner.scripts.command_line_client import (
            get_datasets_from_file,
            get_logging_level,
            read_json_file,
            CCITaggerCommandLineClient
        )

    def test_general(self):
        from cci_tag_scanner.facets import Facets, Concept
        from cci_tag_scanner.tagger import ProcessDatasets
