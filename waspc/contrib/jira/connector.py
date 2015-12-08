from django.conf import settings
from jira import JIRA, JIRAError


class Singleton(object):
    def __init__(self, cls):
        self.cls = cls   # class which is being decorated
        self.instance = None  # instance of that class

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            # new instance is created and stored for future use
            self.instance = self.cls(*args, **kwargs)
        return self.instance


@Singleton
class APIConnector(object):
    def __init__(self):
        jira_settings = settings.WASPC['reporting']['jira']
        self._connection = JIRA(
            server=jira_settings['server'],
            basic_auth=(
                jira_settings['username'],
                jira_settings['password']
            ),
            options=jira_settings['options']
        )
        self._project = jira_settings['project']

    def __dir__(self):
        return dir(self._connection)

    def __getattr__(self, item):
        return getattr(self._connection, item)
