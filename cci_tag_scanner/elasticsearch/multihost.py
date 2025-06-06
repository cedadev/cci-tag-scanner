from elasticsearch import Elasticsearch

class ElasticsearchMH:
    """
    Elasticsearch wrapper for multiple hosts with differing configuration requirements
    """

    # .ceda.ac.uk method
    # External method

    def __init__(self, hosts: list, api_key: str, **kwargs):

        self._int_hosts = [i for i in hosts if 'ceda.ac.uk' in i]
        self._ext_hosts = [i for i in hosts if not 'ceda.ac.uk' in i]

        self._internal = Elasticsearch(
            hosts=self._int_hosts,
            headers = {'x-api-key': api_key},
            **kwargs)
        
        self._external = Elasticsearch(
            hosts=self._ext_hosts,
            api_key=api_key,
            **kwargs
        )

    def _debug_connection(self, check_index: str, id: str):
        """
        Check connection by determining if the index exists on internal/external hosts.
        """
        print(f'DEBUG ext. - Connect to {check_index}: {self._external.exists(index=check_index, id=id)}')
        print(f'DEBUG int. - Connect to {check_index}: {self._internal.exists(index=check_index, id=id)}')

    def count(self, *args, **kwargs) -> dict:
        """
        Wrapper for count method
        """

        c1 = self._external.count(*args, **kwargs)
        c2 = self._internal.count(*args, **kwargs)

        if c1['count'] != c2['count']:
            raise ValueError(
                "WARNING: Disparity between internal/external indexes."
                f"Internal: {c1['count']}"
                f"External: {c2['count']}"
            )
    
        return c1

    def update(self, )