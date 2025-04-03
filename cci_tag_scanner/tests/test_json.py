from cci_tag_scanner.facets import Facets

class TestJSON:
    def test_json_basic(self):
        f1 = Facets()
        assert len(f1.facets) >= len(f1.FACET_ENDPOINTS)

    def test_json_load(self):
        f1 = Facets.from_json('cci_tag_scanner/tests/facet_mappings.json')
        assert len(f1.facets) >= len(f1.FACET_ENDPOINTS)