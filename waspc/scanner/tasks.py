from celery import Task
from contextlib import contextmanager
from django.conf import settings
from mock import Mock, patch
from monkey_patch import w3af_core_target_verify_url
from os.path import join as path_join
from sys import prefix


class Scanner(Task):

    name = 'Scanner'

    def __init__(self):
        self._target_url = None
        self._profile_name = settings.WASPC['scanner']['profile_name']
        self._profile_path = path_join(prefix, 'profiles')
        self._report = {}

    def initialize_report(self, plugins):
        self._report = {'vulnerabilities_counter': 0}
        for plugin_type in plugins:
            for plugin_name in plugins[plugin_type]:
                self._report[plugin_name.get_name()] = {
                    'description': plugin_name.get_long_desc(),
                    'vulnerabilities': {
                        'information': {
                            'items': [],
                            'counter': 0,
                        },
                        'low': {
                            'items': [],
                            'counter': 0,
                        },
                        'medium': {
                            'items': [],
                            'counter': 0,
                        },
                        'high': {
                            'items': [],
                            'counter': 0,
                        },
                        'counter': 0,
                    },
                }

    def update_report(self, item):
        try:
            plugin_name = item.get_plugin_name()
            severity = item.get_severity().lower()
            report_vulnerabilities = self._report[plugin_name]['vulnerabilities']
            report_vulnerabilities[severity]['items'].append(unicode(item))
            report_vulnerabilities[severity]['counter'] += 1
            report_vulnerabilities['counter'] += 1
            self._report['vulnerabilities_counter'] += 1
        except AttributeError:
            self._report = item

    def get_report(self):
        return self._report

    @patch('w3af.core.controllers.w3afCore.w3afCore.WORKER_THREADS', settings.WASPC['scanner']['worker_threads'])
    @patch('w3af.core.controllers.core_helpers.target.CoreTarget._verify_url', w3af_core_target_verify_url)
    @patch('w3af.core.data.parsers.parser_cache.dpc', Mock(name='dpc'), create=True)
    @patch('w3af.core.data.parsers.mp_document_parser.mp_doc_parser', Mock(name='mp_doc_parser'), create=True)
    def scan(self):
        from w3af.core.controllers.w3afCore import w3afCore, kb

        @contextmanager
        def w3af_core():
            instance = w3afCore()
            yield instance
            instance.quit()

        with w3af_core() as core:
            try:
                core.profiles.use_profile(profile_name=self._profile_name,
                                          workdir=self._profile_path)
                target_options = core.target.get_options()
                target_options['target'].set_value(self._target_url)
                core.target.set_options(target_options)
                core.plugins.init_plugins()
                self.initialize_report(core.plugins.plugins)
                core.verify_environment()

                core.start()

                for information_disclosure in kb.get_all_infos():
                    self.update_report(information_disclosure)
                for vulnerability in kb.get_all_vulns():
                    self.update_report(vulnerability)
            except Exception as exception:
                # exc_type - exception type, exc_message - exception message
                # celery's got the same parameters when exception occurs
                # TODO: need to log that event
                # self.update_report(
                #     {
                #         'exc_type': exception.__class__.__name__,
                #         'exc_message': unicode(exception)
                #     }
                # )
                self._report = None

    def run(self, target_url):
        self._target_url = target_url

        self.scan()
        report = self.get_report()

        return {
            'target_url': target_url,
            'report': report
        }
