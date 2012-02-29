import requests
import simplejson

search_url = "%s/rest/api/%s/search?jql="

class BasicAuth:
    def __init__(self, credentials):
        self._cookies = credentials

    @property
    def cookies(self):
        return self._cookies

class Jira:
    """Jira class to interact with Atlassian's issue tracker."""

    __name__ = 'Jira'
    def __init__(self, base_uri=None, api='latest',
                 credentials=None, verify=True):
        """Generic initialization, generally not called directly."""

        self._base_uri = base_uri
        self._api = api
        self._verify = verify
        self._credentials = credentials
    
    def _build_uri(self, **kwargs):
        search_uri = search_url % (self._base_uri,
                                   self._api)
        if 'status' in kwargs:
            status = kwargs['status']
        else:
            status = 'Open'
        search_uri += 'status=' + status                           

        if 'user' in kwargs and 'search_type' in kwargs:
            search_uri += ' and ' + kwargs['search_type'] + '=' + kwargs['user']

        if 'priority' in kwargs:
            search_uri += ' and  priority=' + kwargs['priority']
        return search_uri

    @classmethod
    def login_basic_auth(cls, base_uri=None, api='latest',
                         user=None, password=None,
                         verify=True):
        """
        Basic authentication login mechanism sending user
        and password.

        Keyword arguments:
        user -- user to login with (default None)
        password -- associated password the user has (default None)
        verify -- when using https, verifies certs (default True)
        base_uri -- Jira base uri to connecto to (default None)
        api -- Jira API version to use (default 'latest')

        """
        auth_uri = base_uri + '/rest/auth/latest/session'
        auth = requests.auth.HTTPBasicAuth(user, password)
        response = requests.get(auth_uri, auth=auth, verify=verify)
        credentials = None

        if response.ok:
            credentials = BasicAuth(response.cookies)

        return cls(base_uri, api, credentials, verify)

    def search(self, **kwargs):
        """Generic Jira searching mechanism layering jql."""
        search_uri = self._build_uri(**kwargs)
        
        cookies = None
        if isinstance(self._credentials, BasicAuth):
            cookies = self._credentials.cookies

        return simplejson.loads(requests.get(search_uri,
                                             cookies=cookies,
                                             verify=self._verify).content)

    @property
    def assigned_to_me(self):
        """ Search for issues assigned to logged in user."""
        return self.search(search_type='assignee', user='currentUser()')

    @property
    def reported_by_me(self):
        """ Search for issues reported by logged user."""
        return self.search(search_type='assignee', user='currentUser()')
        
