import json
from globus_sdk.response import GlobusHTTPResponse


class OAuthTokenResponse(GlobusHTTPResponse):
    """
    Class for responses from the OAuth2 code for tokens exchange used in
    3-legged OAuth flows.
    """
    def __init__(self, *args, **kwargs):
        GlobusHTTPResponse.__init__(self, *args, **kwargs)
        # dict used to avoid re-computing self.by_resource_server
        self._by_resource_server = None

    @property
    def by_resource_server(self):
        """
        Representation of the token response in a ``dict`` indexed by resource
        server.

        Although ``OAuthTokenResponse.data`` is still available and
        valid, this representation is typically more desirable for applications
        doing inspection of access tokens and refresh tokens.
        """
        def _mk_item(source_dict):
            """
            Extract a set of fields into a new dict, allow for 'refresh_token'
            to be `None` when absent.
            """
            return {
                'scope': source_dict['scope'],
                'access_token': source_dict['access_token'],
                'refresh_token': source_dict.get('refresh_token'),
                'expires_in': source_dict['expires_in']
            }

        # memoize the results of this property computation in
        # '_by_resource_server'
        if self._by_resource_server is None:
            # call the helper at the top level
            self._by_resource_server = {
                self.resource_server: _mk_item(self)}
            # call the helper on everything in 'other_tokens'
            self._by_resource_server.update(dict(
                (unprocessed_item['resource_server'],
                 _mk_item(unprocessed_item))
                for unprocessed_item in self.other_tokens))

        return self._by_resource_server

    @property
    def expires_in(self):
        """
        The ``expires_in`` value for the top-level token in the response.
        """
        return self['expires_in']

    @property
    def access_token(self):
        """
        The ``access_token`` value for the top-level token in the response.
        """
        return self['access_token']

    @property
    def refresh_token(self):
        """
        The ``refresh_token`` value for the top-level token in the response.
        """
        return self.get('refresh_token')

    @property
    def resource_server(self):
        """
        The ``resource_server`` value for the top-level token in the response.
        """
        return self['resource_server']

    @property
    def other_tokens(self):
        """
        The array of tokens other than the top-level one.
        """
        return self['other_tokens']

    def __str__(self):
        # Make printing responses more convenient by only showing the
        # (typically important) token info
        return json.dumps(self.by_resource_server, indent=2)
